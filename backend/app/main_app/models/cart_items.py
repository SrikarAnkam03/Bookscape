from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class CartItems(db.Model):
    __tablename__ = 'cart_items'

    cart_item_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cart.cart_id'), nullable=False)
    book_id = db.Column(UUID(as_uuid=True), db.ForeignKey('books.book_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    cart = db.relationship('Cart', back_populates='cart_items')
    book = db.relationship('Books', back_populates='cart_items')

    def __init__(self, **kwargs):
        super(CartItems, self).__init__(**kwargs)
