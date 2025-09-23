from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.courses.dao import CourseDAO
from src.courses.models import Course
from src.payment.dto import PaymentResult
from src.payment.models import Payment
from src.payment.schemas import CreatePaymentRequestSchema
from src.payment.services.providers.base import AbstractProvider
from src.payment.services.providers.factory import PaymentProviderFactory
from src.users import User

type PaymentDAO = BaseDAO[Payment, CreatePaymentRequestSchema]


class PaymentService(BaseService):
    """Service class for handling payment operations and transactions.

    This service manages the creation and processing of payments for course
    purchases using configured payment providers. It coordinates between the
    payment provider, database storage, and related course information to
    ensure proper payment processing and record keeping.

    The service abstracts payment provider details through a provider factory
    pattern, allowing for different payment methods and providers while
    maintaining a consistent interface for the application.

    Key responsibilities:
    - Creating and processing new payments
    - Interacting with payment providers
    - Maintaining payment records in the database
    - Coordinating payment information with course purchases
    """

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
            payment_dao (PaymentDAO | None): Optional DAO for payments.
                If not provided, a new PaymentDAO is created.
            course_dao (CourseDAO | None): Optional DAO for courses.
                If not provided, a new CourseDAO is created.
            payment_provider (AbstractProvider | None): Payment service.
                If not provided, a provider is created using factory based.

        """
        super().__init__(db_session)
        self._payment_dao: PaymentDAO = payment_dao or BaseDAO[
            Payment, CreatePaymentRequestSchema
        ](session=db_session, model=Payment)
        self._course_dao: CourseDAO = course_dao or CourseDAO(
            db_session,
            Course,
        )
        self._payment_provider: AbstractProvider = (
            payment_provider or PaymentProviderFactory.create_provider()
        )

    async def create_payment(
        self,
        payment_schema: CreatePaymentRequestSchema,
        course: Course,
        user: User,
    ) -> Payment:
        """Create a new payment record for a course purchase.

        This method creates a payment using the specified payment provider and
        stores the payment record in the database. The payment amount
        and currency are taken from the course details.

        Args:
            payment_schema (CreatePaymentRequestSchema): Schema with payment
                details including payment method.
            course (Course): The course being purchased.
            user (User): The user making the purchase.

        Returns:
            Payment: The created payment record with provider payment ID.

        """
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
