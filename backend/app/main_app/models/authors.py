from app.main_app import db
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Authors(db.Model):
    __tablename__ = 'authors'
    
    author_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_name = db.Column(db.String(255), nullable=False, unique=True)
    author_bio = db.Column(db.Text)
    

    # Define bidirectional relationship
    books = relationship('Books', back_populates='author')


    def __init__(self, **kwargs):
        super(Authors, self).__init__(**kwargs)



        