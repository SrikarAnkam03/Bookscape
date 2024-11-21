from app.main_app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class Roles(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = db.Column(db.String(50), nullable=False)

    user = relationship('Users', back_populates='role')

    def __init__(self, **kwargs):
        super(Roles, self).__init__(**kwargs)