from datetime import datetime, timezone
import uuid
from app.main_app import db
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

def get_current_datetime():
    return datetime.now()

class Users(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    users_pswd = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.role_id'))
    created_at = db.Column(db.DateTime, default=get_current_datetime)
    approve = db.Column(db.Boolean, nullable=False, default=False)
    is_delete = db.Column(db.Boolean, default=False)
    
    role = db.relationship('Roles', back_populates='user')
    addresses = db.relationship('Addresses', back_populates='user', lazy=True)
    wishlists = db.relationship('Wishlist', back_populates='user', lazy=True)
    cart = db.relationship('Cart', back_populates='user', lazy=True)
    wallets = db.relationship('Wallet', back_populates='user', lazy=True)
    books = db.relationship('Books', back_populates='user', lazy=True)
    orders = db.relationship('Orders', back_populates='user',lazy=True)
    review = db.relationship('Reviews', back_populates='user')

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.users_pswd = generate_password_hash(password, salt_length=10)

    def verify_password(self, password):
        return check_password_hash(self.users_pswd, password)

