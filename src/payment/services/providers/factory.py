from src.payment.enums import PaymentProviderEnum
from src.payment.services.providers.base import AbstractProvider
from src.payment.services.providers.stripe import StripePaymentProviderService
from src.settings import Settings


class PaymentProviderFactory:
    """Factory for creating payment providers based on configuration."""
    
    @staticmethod
    def create_provider(provider_type: PaymentProviderEnum | None = None) -> AbstractProvider:
        """Create payment provider instance.
        
        Args:
            provider_type: Specific provider type. If None, uses settings.
            
        Returns:
            AbstractProvider: Payment provider instance.
            
        Raises:
            ValueError: If provider type is unknown.
            NotImplementedError: If provider is not implemented yet.
        """
        if provider_type is None:
            # Берем из настроек (уже enum)
            settings = Settings.load()
            provider_type = settings.payment_settings.PROVIDER
        
        if provider_type == PaymentProviderEnum.STRIPE:
            return StripePaymentProviderService()
        elif provider_type == PaymentProviderEnum.PAYPAL:
            # return PayPalPaymentProviderService()
            raise NotImplementedError("PayPal provider not implemented yet")
        elif provider_type == PaymentProviderEnum.LIQPAY:
            # return LiqPayPaymentProviderService()
            raise NotImplementedError("LiqPay provider not implemented yet")
        elif provider_type == PaymentProviderEnum.WAYFORPAY:
            # return WayForPayPaymentProviderService()
            raise NotImplementedError("WayForPay provider not implemented yet")
        
        raise ValueError(f"Unknown payment provider: {provider_type}")
    
    @classmethod
    def get_available_providers(cls) -> list[PaymentProviderEnum]:
        """Get list of available payment providers.
        
        Returns:
            List of available provider types.
        """
        return [
            PaymentProviderEnum.STRIPE,
            # PaymentProviderEnum.PAYPAL,  # Uncomment when implemented
            # PaymentProviderEnum.LIQPAY,  # Uncomment when implemented
            # PaymentProviderEnum.WAYFORPAY,  # Uncomment when implemented
        ]
