from flask_restx import Resource
from flask import request
from app.main_app import db
import re
from app.main_app.models.users import Users
from app.main_app.models.roles import Roles
from app.main_app.dto.users import UsersDto
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

def hash_password(password):
    return generate_password_hash(password)


signup_blueprint = UsersDto.signupapi
loginapi_blueprint = UsersDto.loginapi
updatedetailsapi_blueprint = UsersDto.updatedetailsapi
getdetailsapi_blueprint = UsersDto.getdetailsapi
listusers_blueprint = UsersDto.listusersapi
userapi_blueprint = UsersDto.userapi

# USER SIGNUP
@signup_blueprint.route('', methods=['POST'])
class Signup(Resource):
    def post(self):
        try:
            # Retrieve data from request
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

            # Username validation
            if not username or len(username) < 3:
                return {'message': 'Username must be at least 3 characters long'}, 400

            # Email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
            if not re.match(email_pattern, email):
                return {'message': 'Invalid email format'}, 400

            # Phone number validation
            if not phone_number.isdigit() or len(phone_number) != 10:
                return {'message': 'Phone number must be exactly 10 digits'}, 400

            # Password validation (length, upper, digit, special character)

            # if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*]', password):
            #     return {
            #         'message': 'Password must be at least 8 characters long, include a number, an uppercase letter, and a special character'
            #     }, 400
            
            if len(password) < 8:
                return {'message': 'Password must be at least 8 characters long'}, 400

            # Confirm password validation
            if password != confirm_password:
                return {'message': 'Passwords do not match'}, 400

            # Check if the user already exists
            user = Users.query.filter_by(email=email).first()
            if user:
                return {'message': 'User already exists with this email'}, 400

            # Check if role exists
            role = Roles.query.filter_by(role='User').first()
            if not role:
                return {'message': 'User role not found'}, 500

            # Create new user
            new_user = Users(
                username=username,
                email=email,
                phone_number=phone_number,
                role_id=role.role_id,
                approve=True
            )
            new_user.password = password  

            # Save the user to the database
            try:
                db.session.add(new_user)
                db.session.commit()
            except Exception as db_error:
                db.session.rollback()
                return {'message': f'Database error: {str(db_error)}'}, 500

            return {'message': 'User created successfully', 'user_id': str(new_user.user_id)}, 201

        except KeyError as key_error:
            # Handle missing fields in the request
            return {'message': f'Missing key: {str(key_error)}'}, 400
        except ValueError as value_error:
            # Handle invalid value conversions (e.g., if data is not in the correct format)
            return {'message': f'Invalid value: {str(value_error)}'}, 400
        except TypeError as type_error:
            # Handle invalid data types
            return {'message': f'Invalid data type: {str(type_error)}'}, 400
        except re.error as regex_error:
            # Handle regex errors
            return {'message': f'Regex error: {str(regex_error)}'}, 400
        except Exception as e:
            # Catch any unexpected exceptions
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Login
@loginapi_blueprint.route('', methods=['POST'])
class Login(Resource):
    def post(self):
        try:
            # Retrieve data from request
            data = request.get_json()
            if not data:
                return {'message': 'Request body is empty'}, 400

            email = data.get('email', '').strip()
            password = data.get('password', '')

            if not email or not password:
                return {'message': 'Email and password are required'}, 400

            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
            if not re.match(email_pattern, email):
                return {'message': 'Invalid email format'}, 400

            # Fetch the user from the database
            user = Users.query.filter_by(email=email).first()
            if not user:
                return {'message': 'Invalid email'}, 404

            # Verify password
            if not user.verify_password(password):
                return {'message': 'Incorrect password'}, 401

            # Check if the user has been approved
            if not user.approve:
                return {'message': 'Admin approval required. Please wait.'}, 403

            # Generate access token
            access_token = create_access_token(identity=user.user_id)

            # Fetch user role
            role = Roles.query.filter_by(role_id=user.role_id).first()
            role_name = role.role if role else 'Unknown'

            return {
                'message': 'Login successful',
                'user_id': str(user.user_id),
                'role_name': role_name,
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'access_token': access_token
            }, 200

        except AttributeError as e:
            # Handle AttributeError, likely due to missing attributes in the data or user object
            return {'message': f'Missing or invalid attribute: {str(e)}'}, 400
        
        except KeyError as e:
            # Handle missing keys in request data
            return {'message': f'Missing key: {str(e)}'}, 400

        except Exception as e:
            # Catch all other unexpected exceptions
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Get User Details
@getdetailsapi_blueprint.route('', methods=['GET'])
class GetUser(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'User identity not found in the token'}, 400

            # Fetch user details from the database
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Prepare the user data for the response
            user_data = {
                'user_id': str(user.user_id),
                'username': user.username,
                'email': user.email,
                'phone_number': user.phone_number,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

            return user_data, 200

        except Exception as e:
            # Catch any unexpected exceptions
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Update User Profile
@updatedetailsapi_blueprint.route('', methods=['PUT'])
class UpdateUser(Resource):
    @jwt_required()
    def put(self):
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'User identity not found in the token'}, 400

            # Get the incoming data from the request
            data = request.get_json()

            if not data:
                return {'message': 'No data provided for update'}, 400

            # Fetch the user from the database
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Update user details with provided data (fallback to current value if not provided)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.phone_number = data.get('phone_number', user.phone_number)

            # Commit the changes to the database
            db.session.commit()

            return {'message': 'Profile updated successfully'}, 200

        except Exception as e:
            # Catch any unexpected exceptions
            db.session.rollback()  # Rollback the session in case of any error
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# Change Password
@userapi_blueprint.route('/change-password', methods=['PUT'])
class UpdateUserPassword(Resource):
    @jwt_required()
    def put(self):
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'User identity not found in the token'}, 400

            # Get the incoming data from the request
            data = request.get_json()

            if not data:
                return {'message': 'No data provided'}, 400

            current_password = data.get('current_password')
            new_password = data.get('new_password')

            if not current_password or not new_password:
                return {'message': 'Both current and new password are required'}, 400

            # Fetch the user from the database
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Verify the current password
            if not user.verify_password(current_password):
                return {'message': 'Incorrect password'}, 401

            # Update the password
            user.password = new_password
            db.session.commit()

            return {'message': 'Password changed successfully'}, 200

        except Exception as e:
            # Catch any unexpected exceptions
            db.session.rollback()  # Rollback the session in case of any error
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# List Users (Admin)
@listusers_blueprint.route('', methods=['GET'])
class AdminUsers(Resource):
    def get(self):
        try:
            # Try to get the 'User' role from the Roles table
            role = Roles.query.filter_by(role='User').first()

            # If the role is not found, return an error message
            if not role:
                return {'status': 'error', 'message': 'User role not found'}, 404

            # Try to get users with the 'User' role, ordered by creation date (descending)
            users = Users.query.filter_by(role_id=role.role_id).order_by(Users.created_at.desc()).all()

            # If no users are found, return an empty list
            if not users:
                return {'status': 'success', 'data': []}, 200

            # Prepare the list of users to return
            user_list = [
                {
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
                for user in users
            ]

            # Return the list of users with a success status
            return {'status': 'success', 'data': user_list}, 200

        except Exception as e:
            # Handle any unexpected errors (e.g., database connection issues)
            return {'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, 500
