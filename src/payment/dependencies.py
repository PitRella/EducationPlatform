from fastapi import Depends
from src.payment.services.providers.base import AbstractProvider
from src.payment.services.providers.factory import PaymentProviderFactory
from src.payment.enums import PaymentProviderEnum


def get_payment_provider() -> AbstractProvider:
    """Get payment provider based on settings.
    
    Returns:
        AbstractProvider: Configured payment provider instance.
    """
    return PaymentProviderFactory.create_provider()


def get_payment_provider_by_type(provider_type: PaymentProviderEnum) -> AbstractProvider:
    """Get specific payment provider by type.
    
    Args:
        provider_type: Payment provider type enum.
        
    Returns:
        AbstractProvider: Payment provider instance.
        
    Raises:
        ValueError: If provider type is unknown.
    """
    return PaymentProviderFactory.create_provider(provider_type)


def get_available_providers() -> list[str]:
    """Get list of available payment providers.
    
    Returns:
        List of available provider names.
    """
    providers = PaymentProviderFactory.get_available_providers()
    return [provider.value for provider in providers]
