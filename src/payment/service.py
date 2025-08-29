from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.payment.models import Payment
from src.base.service import BaseService
from src.payment.schemas import CreatePaymentRequestSchema

type PaymentDAO = BaseDAO[Payment, CreatePaymentRequestSchema]


class PaymentService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            dao: PaymentDAO | None = None,
    ) -> None:
        """Initialize the LessonService.

        Args:
            db_session (AsyncSession): SQLAlchemy async database session.
            dao (LessonDAO | None): Optional data access object for lessons.
                If not provided, a new LessonDAO is created.

        """
        super().__init__(db_session)
        self._dao: PaymentDAO = dao or BaseDAO[
            Payment,
            CreatePaymentRequestSchema
        ](session=db_session, model=Payment,)
