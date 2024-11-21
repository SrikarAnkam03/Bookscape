from sqlalchemy import CheckConstraint
from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
from app.main_app.models.authors import Authors
import uuid
from datetime import datetime

class Books(db.Model):
    __tablename__ = 'books'
    
    book_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False, unique=True)
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey('authors.author_id'), nullable=False)
    genre_id = db.Column(UUID(as_uuid=True), db.ForeignKey('genres.genre_id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    published_date = db.Column(db.Date)  
    cover_image_url = db.Column(db.Text)
    description = db.Column(db.Text)
    isbn = db.Column(db.String(20))
    rating = db.Column(db.Numeric(3, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    display = db.Column(db.Boolean, default=True, nullable=False)
    is_delete = db.Column(db.Boolean, default=False, nullable=False)  # Default changed to False

    user = db.relationship('Users', back_populates='books')
    author = db.relationship('Authors', back_populates='books')
    genre = db.relationship('Genres', back_populates='books')
    wishlist_items = db.relationship('WishlistItems', back_populates='book')
    cart_items = db.relationship('CartItems', back_populates='book')
    order_items = db.relationship('OrderItems', back_populates='book')
    review = db.relationship('Reviews', back_populates='book')

    __table_args__ = (
        CheckConstraint('stock >= 0 AND stock <= 150', name='check_stock_limit'),
    )

    def __init__(self, **kwargs):
        super(Books, self).__init__(**kwargs)
