from typing import Optional
from app.services.billing.gateways.base import PaymentGateway
from app.services.billing.gateways.stripe_gateway import StripeGateway
from app.services.billing.gateways.razorpay_gateway import RazorpayGateway
from app.services.billing.gateways.mock_gateway import MockGateway


def get_payment_gateway(provider: Optional[str] = None) -> PaymentGateway:
    """
    Factory function returning requested payment gateway implementation.
    Defaults to STRIPE if not specified or unrecognized.
    """
    if not provider:
        provider = "STRIPE"

    provider_clean = provider.strip().upper()

    if provider_clean == "STRIPE":
        return StripeGateway()
    elif provider_clean == "RAZORPAY":
        return RazorpayGateway()
    elif provider_clean == "MOCK":
        return MockGateway()
    else:
        return StripeGateway()
