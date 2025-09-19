from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dao import BaseDAO
from src.base.service import BaseService
from src.payment.dto import StripeWebhookPayload
from src.payment.enums import PaymentStatusEnum
from src.payment.models import Payment
from src.payment.schemas import CreatePaymentRequestSchema
from src.payment.services.payment import PaymentDAO
import logging

logger = logging.getLogger(__name__)


class StripeWebhookService(BaseService):
    def __init__(
            self,
            db_session: AsyncSession,
            payment_dao: PaymentDAO | None = None,
    ) -> None:
        super().__init__(db_session)
        self._payment_dao: PaymentDAO = payment_dao or BaseDAO[
            Payment,
            CreatePaymentRequestSchema
        ](session=db_session, model=Payment)

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
        async with self.session.begin():
            payment: Payment | None = await self._payment_dao.update(
                {"status": payment_status},
                provider_payment_id=payment_id,
            )
        if not payment:
            logger.warning(f"Payment with id %s not found", payment_id)
