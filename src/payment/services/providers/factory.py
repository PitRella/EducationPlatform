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
            settings = Settings.load()
            provider_type = settings.payment_settings.PROVIDER
        
        match provider_type:
            case PaymentProviderEnum.STRIPE:
                return StripePaymentProviderService()
            case PaymentProviderEnum.PAYPAL:
                raise NotImplementedError("PayPal provider not implemented yet")
            case PaymentProviderEnum.LIQPAY:
                raise NotImplementedError("LiqPay provider not implemented yet")
            case PaymentProviderEnum.WAYFORPAY:
                raise NotImplementedError("WayForPay provider not implemented yet")
            case _:
                raise ValueError(f"Unknown payment provider: {provider_type}")
    
    @classmethod
    def get_available_providers(cls) -> list[PaymentProviderEnum]:
        """Get list of available payment providers.
        
        Returns:
            List of available provider types.
        """
        return [
            PaymentProviderEnum.STRIPE,
            # PaymentProviderEnum.PAYPAL,  # TODO: Uncomment when implemented
            # PaymentProviderEnum.LIQPAY,  # TODO: Uncomment when implemented
            # PaymentProviderEnum.WAYFORPAY,  # TODO: Uncomment when implemented
        ]
