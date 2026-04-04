from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from app.models.order import Order
from app.models.user import User
from datetime import datetime

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email",
)

fastmail = FastMail(conf)


async def send_order_confirmation_email(order: Order, user: User):
    """
    Sends an order confirmation email to the customer.
    """
    message = MessageSchema(
        subject=f"Order Confirmed - {order.id}",
        recipients=[user.email],
        template_body={
            "order_id": str(order.id),
            "items": order.items,
            "total_amount": order.total_amount,
            "current_year": datetime.now().year,
        },
        subtype=MessageType.html,
    )
    
    await fastmail.send_message(message, template_name="order_confirmation.html")


async def send_new_order_admin_alert(order: Order, user: User):
    """
    Sends an alert email to the admin for a new order.
    """
    if not settings.ADMIN_EMAIL:
        return

    message = MessageSchema(
        subject=f"New Order Alert - {order.id}",
        recipients=[settings.ADMIN_EMAIL],
        template_body={
            "order_id": str(order.id),
            "customer_name": user.full_name or "Customer",
            "customer_email": user.email,
            "total_amount": order.total_amount,
        },
        subtype=MessageType.html,
    )
    
    await fastmail.send_message(message, template_name="new_order_alert.html")
