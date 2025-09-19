from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.payment.dto import StripeWebhookPayload
from src.payment.enums import PaymentStatusEnum
from src.payment.models import Payment
from src.payment.schemas import CreatePaymentRequestSchema
from src.payment.services.payment import PaymentDAO
import logging

from src.users.models import UserCourses

logger = logging.getLogger(__name__)

type UserCourseDAO = BaseDAO[UserCourses]


class StripeWebhookService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            payment_dao: PaymentDAO | None = None,
            user_courses_dao: UserCourseDAO | None = None,

    ) -> None:
        super().__init__(db_session)
        self._payment_dao: PaymentDAO = payment_dao or BaseDAO[
            Payment,
            CreatePaymentRequestSchema
        ](session=db_session, model=Payment)
        self._user_courses_dao: UserCourseDAO = user_courses_dao or BaseDAO[
            UserCourses
        ](db_session, model=UserCourses)

    async def handle_webhook(
            self,
            request_body: bytes
    ) -> None:
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
                    {"status": payment_status},
                    provider_payment_id=payment_id,
                )
                if not payment:
                    logger.warning(
                        "Payment with id %s not found",
                        payment_id
                    )
                    return
                if payment_status == PaymentStatusEnum.SUCCEEDED:
                    bought_course: (
                            UserCourses | None
                    ) = await self._user_courses_dao.create(
                        {
                            'user_id': payment.user_id,
                            'course_id': payment.course_id
                        }
                    )
                    if not bought_course:
                        logger.error(
                            "Course %s was not bought by user %s",
                            payment.course_id,
                            payment.user_id
                        )
                        return
                    logger.info(
                        "Course %s was bought by user %s",
                        bought_course.course_id,
                        bought_course.user_id
                    )
        except IntegrityError:
            logger.error("Course was already bought by user")
            return
