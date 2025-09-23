import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.payment.dto import StripeWebhookPayload
from src.payment.enums import PaymentStatusEnum
from src.payment.models import Payment
from src.payment.schemas import CreatePaymentRequestSchema
from src.payment.services.payment import PaymentDAO
from src.users.models import UserCourses

logger = logging.getLogger(__name__)

type UserCourseDAO = BaseDAO[UserCourses]


class StripeWebhookService(BaseService):
    """Service for handling Stripe webhook notifications.

    This service processes incoming webhook notifications from
    a Stripe payment system, updates payment statuses in the database,
    and manages course access upon successful payment completion.

    Args:
        db_session (AsyncSession): SQLAlchemy async database session.
        payment_dao (PaymentDAO | None, optional): DAO for payment operations.
            If None, a new BaseDAO[Payment] instance is created. Default None.
        user_courses_dao (UserCourseDAO | None, optional): DAO for user courses
            operations. If None, a new BaseDAO[UserCourses] instance is created.
            Defaults to None.

    """

    def __init__(
        self,
        db_session: AsyncSession,
        payment_dao: PaymentDAO | None = None,
        user_courses_dao: UserCourseDAO | None = None,
    ) -> None:
        """Initialize the StripeWebhookService.

        Creates a new instance of the StripeWebhookService with the provided
        database session and DAOs. If DAOs are not provided, creates new
        instances using the session.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.
            payment_dao (PaymentDAO | None, optional): DAO for payments.
                If None, a new BaseDAO[Payment] instance is created.
                Defaults to None.
            user_courses_dao (UserCourseDAO | None, optional): DAO for user
                courses operations. If None, a new BaseDAO[UserCourses] instance
                is created. Defaults to None.

        """
        super().__init__(db_session)
        self._payment_dao: PaymentDAO = payment_dao or BaseDAO[
            Payment, CreatePaymentRequestSchema
        ](session=db_session, model=Payment)
        self._user_courses_dao: UserCourseDAO = user_courses_dao or BaseDAO[
            UserCourses
        ](db_session, model=UserCourses)

    async def handle_webhook(self, request_body: bytes) -> None:
        """Process incoming Stripe webhook request.

        This method handles incoming webhook notifications from Stripe,
        updates the payment status in the database, and if the payment
        was successful, creates a new user course relationship.

        Args:
            request_body (bytes): Raw webhook request body from Stripe.

        Returns:
            None

        Raises:
            IntegrityError: If the course was already purchased by the user.

        """
        payload: StripeWebhookPayload = StripeWebhookPayload.from_body(
            request_body
        )
        payment_id: str = payload.data.object.id
        payment_status: PaymentStatusEnum = PaymentStatusEnum(
            payload.data.object.status
        )
        try:
            async with self.session.begin():
                payment: Payment | None = await self._payment_dao.update(
                    {'status': payment_status},
                    provider_payment_id=payment_id,
                )
                if not payment:
                    logger.warning('Payment with id %s not found', payment_id)
                    return
                if payment_status == PaymentStatusEnum.SUCCEEDED:
                    bought_course: (
                        UserCourses | None
                    ) = await self._user_courses_dao.create(
                        {
                            'user_id': payment.user_id,
                            'course_id': payment.course_id,
                        }
                    )
                    if not bought_course:
                        logger.error(
                            'Course %s was not bought by user %s',
                            payment.course_id,
                            payment.user_id,
                        )
                        return
                    logger.info(
                        'Course %s was bought by user %s',
                        bought_course.course_id,
                        bought_course.user_id,
                    )
        except IntegrityError:
            logger.exception('Course was already bought by user')
            return
