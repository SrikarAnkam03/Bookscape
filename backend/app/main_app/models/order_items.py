from datetime import datetime
import pytz
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import TIMESTAMP, Integer, Numeric
from sqlalchemy.orm import relationship
from app.main_app import db
import uuid

class OrderItems(db.Model):
    __tablename__ = 'order_items'

    order_item_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(UUID(as_uuid=True), db.ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(UUID(as_uuid=True), db.ForeignKey('books.book_id'), nullable=False)
    quantity = db.Column(Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    order_at = db.Column(
        TIMESTAMP(timezone=True), 
        default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')), 
        nullable=False
    )

    orders = relationship('Orders', back_populates='order_items')
    book = relationship('Books', back_populates='order_items')

    def __init__(self, **kwargs):
        super(OrderItems, self).__init__(**kwargs)
