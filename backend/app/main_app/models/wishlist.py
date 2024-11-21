from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.main_app import db
import uuid

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    
    wishlist_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)

    user = relationship('Users', back_populates='wishlists')
    items = relationship('WishlistItems', back_populates='wishlist')

    def __init__(self, **kwargs):
        super(Wishlist, self).__init__(**kwargs)
