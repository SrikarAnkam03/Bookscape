from app.main_app import db
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Genres(db.Model):
    __tablename__ = 'genres'
    
    genre_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    genre_name = db.Column(db.String(100), nullable=False)

    books = relationship('Books', back_populates='genre')

    def __init__(self, **kwargs):
        super(Genres, self).__init__(**kwargs)
