from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

class Reviews(db.Model):
    __tablename__ = 'reviews'
    
    review_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    book_id = db.Column(UUID(as_uuid=True), db.ForeignKey('books.book_id'), nullable=False)
    comment = db.Column(db.String(256), nullable=False)
    rating = db.Column(db.Numeric(3, 2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship('Users', back_populates='review')
    book = db.relationship('Books', back_populates='review')

    __table_args__ = (
        CheckConstraint('rating >= 0 AND rating <= 5', name='check_rating_range'),
    )

    def __init__(self, **kwargs):
        super(Reviews, self).__init__(**kwargs)
