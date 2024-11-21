from datetime import datetime
import uuid
from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID

class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = db.Column(UUID(as_uuid=True), db.ForeignKey('wallet.wallet_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'debit' or 'credit'
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.utcnow)

    wallet = db.relationship('Wallet', back_populates='transactions', lazy=True)  
    

    __table_args__ = (
        db.CheckConstraint("transaction_type IN ('credit', 'debit')", name='check_transaction_type'),
    )