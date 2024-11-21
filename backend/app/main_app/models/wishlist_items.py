from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

class WishlistItems(db.Model):
    __tablename__ = 'wishlist_items'
    
    wishlist_item_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(UUID(as_uuid=True), db.ForeignKey('books.book_id'), nullable=False)
    wishlist_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wishlist.wishlist_id'), nullable=False)
    
    # Define relationships
    book = relationship('Books', back_populates='wishlist_items')
    wishlist = relationship('Wishlist', back_populates='items')
