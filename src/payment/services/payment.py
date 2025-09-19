from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.courses.dao import CourseDAO
from src.courses.enums import CurrencyEnum
from src.courses.exceptions import CourseNotFoundByIdException
from src.courses.models import Course
from src.payment.dto import PaymentResult
from src.payment.models import Payment
from src.base.service import BaseService
from src.payment.schemas import CreatePaymentRequestSchema
from src.payment.services.providers.factory import PaymentProviderFactory
from src.payment.services.providers.base import AbstractProvider
from src.users import User

type PaymentDAO = BaseDAO[Payment, CreatePaymentRequestSchema]


class PaymentService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            payment_dao: PaymentDAO | None = None,
            course_dao: CourseDAO | None = None,
            payment_provider: AbstractProvider | None = None,
    ) -> None:
        """Initialize the PaymentService.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.
            payment_dao (PaymentDAO | None): Optional data access object for payments.
                If not provided, a new PaymentDAO is created.
            course_dao (CourseDAO | None): Optional data access object for courses.
                If not provided, a new CourseDAO is created.
            payment_provider (AbstractProvider | None): Payment provider service.
                If not provided, provider is created using factory based on settings.

        """
        super().__init__(db_session)
        self._payment_dao: PaymentDAO = payment_dao or BaseDAO[
            Payment,
            CreatePaymentRequestSchema
        ](session=db_session, model=Payment)
        self._course_dao: CourseDAO = course_dao or CourseDAO(
            db_session,
            Course,
        )
        self._payment_provider: AbstractProvider = payment_provider or PaymentProviderFactory.create_provider()

    async def create_payment(
            self,
            payment_schema: CreatePaymentRequestSchema,
            course: Course,
            user: User,
    ) -> Payment:
        data = payment_schema.model_dump()
        data['user_id'] = user.id
        data['course_id'] = course.id
        data['amount'] = course.price
        data['currency'] = course.currency
        payment_result: PaymentResult = self._payment_provider.create_payment(
            amount=data['amount'],
            currency=course.currency,
            method=payment_schema.payment_method,
        )
        data['provider_payment_id'] = payment_result.id
        async with self.session.begin():
            payment: Payment = await self._payment_dao.create(data)
        return payment
