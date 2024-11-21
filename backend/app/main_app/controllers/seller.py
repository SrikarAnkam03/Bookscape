from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource
from flask import request
import re
from app.main_app import db
from app.main_app.models.users import Users
from app.main_app.models.roles import Roles
from app.main_app.models.books import Books
from app.main_app.dto.books import BooksDto
from app.main_app.dto.users import UsersDto
from werkzeug.security import generate_password_hash

def hash_password(password):
    return generate_password_hash(password)

sellerapi_blueprint = UsersDto.sellerapi
sellers_blueprint = UsersDto.sellersapi
approveSellerapi_blueprint = UsersDto.approveSellerapi
deleteapi_blueprint = UsersDto.deleteapi


# SIGNUP SELLER
@sellerapi_blueprint.route('', methods=['POST'])
class Signup(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {'message': "Required field is missing"}, 400

        if not all(k in data for k in ("username", "email", "phone_number", "users_pswd", "confirm_password")):
            return {'message': "Required field is missing"}, 400

        username = data.get('username').strip()
        email = data.get('email').strip()
        phone_number = data.get('phone_number').strip()
        password = data.get('users_pswd')
        confirm_password = data.get('confirm_password')

        try:
            # Validate username
            if not username or len(username) < 3:
                return {'message': 'Username must be at least 3 characters long'}, 400
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
            if not re.match(email_pattern, email):
                return {'message': 'Invalid email format'}, 400

            # Validate phone number
            if not phone_number.isdigit() or len(phone_number) != 10:
                return {'message': 'Phone number must be exactly 10 digits'}, 400
            

            # Validate password length

            # if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*]', password):
            #     return {
            #         'message': 'Password must be at least 8 characters long, include a number, an uppercase letter, and a special character'
            #     }, 400
            
            if len(password) < 8:
                return {'message': 'Password must be at least 8 characters long'}, 400

            # Validate password confirmation
            if password != confirm_password:
                return {'message': 'Passwords do not match'}, 400

            # Check if user already exists
            user = Users.query.filter_by(email=email).first()
            if user:
                return {'message': 'User already exists with this email'}, 400

            # Check if the 'Seller' role exists
            role = Roles.query.filter_by(role='Seller').first()
            if not role:
                return {'message': 'User role not found'}, 500

            # Create new user
            new_user = Users(
                username=username,
                email=email,
                phone_number=phone_number,
                role_id=role.role_id
            )
            new_user.password = hash_password(password)

            # Attempt to add new user to the database
            db.session.add(new_user)
            db.session.commit()

            return {'message': 'User created successfully', 'user_id': str(new_user.user_id)}, 201

        except AttributeError as e:
            db.session.rollback()
            return {'message': 'Attribute error occurred: ' + str(e)}, 500

        except ValueError as e:
            db.session.rollback()
            return {'message': 'Value error occurred: ' + str(e)}, 500

        except Exception as e:
            db.session.rollback()
            return {'message': 'An unexpected error occurred: ' + str(e)}, 500


# To Fetch sellers
@sellers_blueprint.route('', methods=['GET'])
class AdminSellers(Resource):
    def get(self):
        try:
            # Check if the 'Seller' role exists
            seller_role = Roles.query.filter_by(role='Seller').first()

            if not seller_role:
                return {'status': 'error', 'message': 'Seller role not found'}, 404

            # Fetch sellers with the 'Seller' role
            sellers = Users.query.filter_by(
                role_id=seller_role.role_id
            ).filter_by(is_delete=False).order_by(Users.created_at.desc()).all()

            # Prepare the response data
            seller_list = [
                {
                    'user_id': str(seller.user_id),
                    'username': seller.username,
                    'email': seller.email,
                    'phone_number': seller.phone_number,
                    'created_at': seller.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'approve': seller.approve
                }
                for seller in sellers
            ]

            return {'status': 'success', 'data': seller_list}, 200

        except AttributeError as e:
            # Catch AttributeErrors (e.g., missing attributes in the query)
            return {'status': 'error', 'message': f'Attribute error: {str(e)}'}, 500

        except ValueError as e:
            # Catch ValueErrors (e.g., invalid values during processing)
            return {'status': 'error', 'message': f'Value error: {str(e)}'}, 500

        except Exception as e:
            # Catch any unexpected errors
            return {'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, 500


# Fetching seller details
@sellerapi_blueprint.route('/<string:username>', methods=['GET'])
class SellerDetails(Resource):
    def get(self, username):
        try:
            # Attempt to fetch the user by username
            user = Users.query.filter_by(username=username).first()

            if user:
                # Prepare the user data if found
                user_data = {
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                return user_data, 200
            else:
                # Return error message if user is not found
                return {'message': 'Seller not found'}, 404

        except AttributeError as e:
            # Catch AttributeError (e.g., issues with missing attributes or database errors)
            return {'message': f'Attribute error: {str(e)}'}, 500

        except Exception as e:
            # Catch any unexpected errors
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Approve Seller
@sellerapi_blueprint.route('/accept', methods=['PUT'])
class AdminApprove(Resource):
    def put(self):
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return {'message': 'user_id is required'}, 400
        
        try:
            # Attempt to fetch the user by user_id
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                # Return error message if user not found
                return {'message': 'User not found'}, 404
            
            # Approve the user
            user.approve = True

            # Fetch the user's books and make them visible if not deleted
            books = Books.query.filter_by(user_id=user_id).all()
            for book in books:
                if not book.is_delete:
                    book.display = True

            # Commit the changes to the database
            db.session.commit()

            return {'message': f'User {user.username} has been approved and their books are now visible'}, 200
        
        except AttributeError as e:
            # Catch AttributeError (e.g., if user or book attributes are missing or invalid)
            db.session.rollback()
            return {'message': f'Attribute error: {str(e)}'}, 500

        except Exception as e:
            # Catch any other unforeseen errors
            db.session.rollback()
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Reject Seller
@sellerapi_blueprint.route('/reject', methods=['PUT'])
class AdminReject(Resource):
    def put(self):
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return {'message': 'user_id is required'}, 400

        try:
            # Attempt to fetch the user by user_id
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                # Return error message if user not found
                return {'message': 'User not found'}, 404
            
            # Reject the user by setting approve to False
            user.approve = False

            # Fetch the user's books and hide them
            books = Books.query.filter_by(user_id=user_id).all()
            for book in books:
                book.display = False

            # Commit the changes to the database
            db.session.commit()

            return {'message': f'User {user.username} has been rejected and their books have been hidden'}, 200
        
        except AttributeError as e:
            # Catch AttributeError (e.g., if user or book attributes are missing or invalid)
            db.session.rollback()
            return {'message': f'Attribute error: {str(e)}'}, 500

        except Exception as e:
            # Catch any other unforeseen errors
            db.session.rollback()
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# To Soft Delete User
@deleteapi_blueprint.route('/<sellerId>', methods=['DELETE'])
class DeleteUser(Resource):
    @jwt_required()
    def delete(self, sellerId):
        try:
            # Attempt to fetch the user by sellerId
            user = Users.query.filter_by(user_id=sellerId).first()

            if user:
                # Mark the user as deleted and hide them
                user.is_delete = True  
                user.display = False

                # Commit the changes to the database
                db.session.commit()
                return {'message': 'Seller deleted successfully'}, 200
            else:
                return {'message': 'User not found'}, 404

        except Exception as e:
            # Handle any errors that may occur during the operation
            db.session.rollback()
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


