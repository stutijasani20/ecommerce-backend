import stripe
from fastapi import APIRouter, Header, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services import stripe_service
from app.services import order as order_service
from app.core.logging_config import setup_logging
import logging


setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe webhook endpoint to handle checkout session completion and payment failure.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe Signature")
    
    payload = await request.body()
    
    try:
        event = stripe_service.verify_webhook_signature(payload, stripe_signature)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid Stripe Signature")
    
    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        
        if order_id:
            logger.info(f"Payment successful for order: {order_id}")
            await order_service.handle_order_payment_success(db, order_id=order_id)
        
    elif event["type"] == "checkout.session.async_payment_failed":
        session = event["data"]["object"]
        order_id = session.get("metadata", {}).get("order_id")
        
        if order_id:
            logger.warning(f"Payment failed for order: {order_id}")
            await order_service.handle_order_cancellation(db, order_id=order_id)
            
    # Add other event types here (e.g., charge.refunded, etc.)
    
    return {"status": "success"}
