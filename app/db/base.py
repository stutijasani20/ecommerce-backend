# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.database import Base  # noqa
from app.models.user import User  # noqa
from app.models.product import Product  # noqa
from app.models.cart import CartItem  # noqa
from app.models.order import Order, OrderItem  # noqa
from app.models.tracking import ShipmentTracking  # noqa
