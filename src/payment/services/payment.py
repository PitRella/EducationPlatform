from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.courses.dao import CourseDAO
from src.courses.exceptions import CourseNotFoundByIdException
from src.courses.models import Course
from src.payment.models import Payment
from src.base.service import BaseService
from src.payment.schemas import CreatePaymentRequestSchema
from src.users import User

type PaymentDAO = BaseDAO[Payment, CreatePaymentRequestSchema]


class PaymentService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            payment_dao: PaymentDAO | None = None,
            course_dao: CourseDAO | None = None,
    ) -> None:
        """Initialize the LessonService.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.
            payment_dao (LessonDAO | None): Optional data access object for lessons.
                If not provided, a new LessonDAO is created.

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

    async def create_payment(
            self,
            payment_schema: CreatePaymentRequestSchema,
            user: User,
    ) -> Payment:
        async with self.session.begin():
            course: Course | None = await self._course_dao.get_published_course(
                id=payment_schema.course_id
            )
        if not course:
            raise CourseNotFoundByIdException
        data = payment_schema.model_dump()
        data['user_id'] = user.id
        data['course_id'] = course.id
        data['amount'] = course.price
        data['currency'] = course.currency
        async with self.session.begin():
            payment: Payment = await self._payment_dao.create(data)
        return payment
