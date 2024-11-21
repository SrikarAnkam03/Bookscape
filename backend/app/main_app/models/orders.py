from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import TIMESTAMP
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

class Orders(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('addresses.address_id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    user = db.relationship('Users', back_populates='orders')
    address = db.relationship('Addresses', back_populates='orders')
    order_items = relationship('OrderItems', back_populates='orders')

    def __init__(self, **kwargs):
        super(Orders, self).__init__(**kwargs)
