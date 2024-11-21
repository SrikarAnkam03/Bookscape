from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class OTP(db.Model):
    __tablename__ = 'otp'
    
    otp_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(120), nullable=False, unique=True)
    otp = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
 
    def __init__(self, email, otp):
        self.email = email
        self.otp = otp
 
    
    def __init__(self, **kwargs):
        super(OTP, self).__init__(**kwargs)