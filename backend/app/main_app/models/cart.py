from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey
from app.main_app import db
import uuid


class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), unique=True, nullable=False)

    cart_items = relationship('CartItems', back_populates='cart')
    user = relationship('Users', back_populates='cart')

    def __init__(self, **kwargs):
        super(Cart, self).__init__(**kwargs)

