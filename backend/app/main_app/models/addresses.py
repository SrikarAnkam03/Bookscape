from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

class Addresses(db.Model):
    __tablename__ = 'addresses'

    address_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    recipient_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    address_type = db.Column(db.String(50), nullable=False)

    user = relationship('Users', back_populates='addresses')
    orders = db.relationship('Orders', back_populates='address')

    def __init__(self, **kwargs):
        super(Addresses, self).__init__(**kwargs)
