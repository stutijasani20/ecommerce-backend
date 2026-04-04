import stripe
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models.order import Order


# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY


async def create_checkout_session(order: Order, user_email: str) -> str:
    """
    Creates a Stripe Checkout Session for the order.
    """
    # Create line items for Stripe
    line_items = []
    for item in order.items:
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.product.name,
                    "description": item.product.description,
                },
                "unit_amount": int(item.price * 100),  # Stripe expects cents
            },
            "quantity": item.quantity,
        })
    
    # Create session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=settings.STRIPE_SUCCESS_URL.format(CHECKOUT_SESSION_ID="{CHECKOUT_SESSION_ID}"),
        cancel_url=settings.STRIPE_CANCEL_URL,
        customer_email=user_email,
        metadata={
            "order_id": str(order.id),
            "user_id": str(order.user_id),
        },
    )
    
    return session.url


def verify_webhook_signature(payload: bytes, sig_header: str) -> Dict[str, Any]:
    """
    Verifies the Stripe webhook signature.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e
