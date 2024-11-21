from datetime import datetime
import uuid
from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
from app.main_app.models.transactions import Transaction

class Wallet(db.Model):
    __tablename__ = 'wallet'
    
    wallet_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationship to users and transactions
    user = db.relationship('Users', back_populates='wallets')
    transactions = db.relationship('Transaction', back_populates='wallet', lazy=True)  


    def __init__(self, **kwargs):
        super(Wallet, self).__init__(**kwargs)