import re
import uuid
from app.main_app.models.users import Users
from app.main_app.models.otp import OTP
from app.main_app.dto.otp import otpDto
from flask_restx import Resource
from datetime import datetime, timedelta
from app.main_app import db
from flask import request
import smtplib
from sqlalchemy.exc import SQLAlchemyError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash

email_regex = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
 
def generate_otp():
    return str(uuid.uuid4().int)[:6] 

sendotp_blueprint = otpDto.otpapi
emailVerification_blueprint = otpDto.emailVerifyOtpapi


#  EMAIL VERIFICATION 

# send OTP
@emailVerification_blueprint.route('/send-emailVerifyOtp', methods=['POST'])
class SendEmailOTP(Resource):
    def post(self):
        try:
            # Fetch data from the request
            data = request.get_json()
            if not data:
                return {"message": "No input data provided"}, 400

            email = data.get('email')
            print(email)

            # Validate email presence
            if not email:
                return {"message": "Please enter the email before submitting"}, 400

            # Validate email format using regex
            if not re.match(email_regex, email):
                return {"message": "Invalid email format"}, 400

            # Check if the email is already registered
            user = Users.query.filter_by(email=email).first()
            if user:
                return {"message": "Email already registered"}, 404

            # Generate OTP and set expiration time (5 minutes from now)
            otp_code = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=5)

            # Check if an OTP entry already exists for this email
            otp_entry = OTP.query.filter_by(email=email).first()
            if otp_entry:
                # If an existing OTP entry is found, delete it
                db.session.delete(otp_entry)
                db.session.commit()

            # Create a new OTP entry
            new_otp = OTP(email=email, otp=otp_code, expires_at=expires_at)
            db.session.add(new_otp)
            db.session.commit()

            # Send the OTP email
            if self.send_email(email, otp_code):
                return {"message": "OTP sent successfully"}, 200
            else:
                return {"message": "Failed to send OTP email"}, 500

        except KeyError as e:
            return {"message": f"Missing key: {str(e)}"}, 400

        except AttributeError as e:
            return {"message": f"Attribute error: {str(e)}"}, 400

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback any uncommitted changes
            return {"message": "Database error occurred", "error": str(e)}, 500

        except smtplib.SMTPAuthenticationError:
            return {"message": "Email authentication failed. Check your email credentials."}, 500

        except smtplib.SMTPException as e:
            return {"message": "Error sending email", "error": str(e)}, 500

        except Exception as e:
            return {"message": "An unexpected error occurred", "error": str(e)}, 500

    def send_email(self, email, otp_code):
        sender_email = "lsoneproject@gmail.com"
        app_password = "kpme ktaz mdhk nhyi"

        subject = "Your OTP Code for Password Reset"
        body = f"Your OTP code is: {otp_code}\nIt is valid for 5 minutes."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Attempt to send the email using SMTP_SSL
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
                return True
        except smtplib.SMTPAuthenticationError:
            print("Failed to authenticate with the SMTP server.")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return False


# verify OTP    
@emailVerification_blueprint.route('/verify-emailVerifyOtp', methods=['POST'])
class VerifyOtp(Resource):
    def post(self):
        try:
            # Get the JSON data from the request
            data = request.json
            if not data:
                return {"message": "No input data provided"}, 400

            email = data.get('email')
            otp_code = data.get('otp')

            # Validate that both email and OTP are provided
            if not email or not otp_code:
                return {"message": "Email and OTP are required"}, 400

            # Fetch the OTP entry from the database
            otp_entry = OTP.query.filter_by(email=email, otp=otp_code).first()

            # Check if the OTP entry exists
            if not otp_entry:
                return {"message": "Invalid OTP"}, 400

            # Check if the OTP has expired
            if otp_entry.expires_at < datetime.now():
                db.session.delete(otp_entry)
                db.session.commit()
                return {"message": "OTP has expired"}, 400

            # OTP is valid, so delete the entry from the database
            db.session.delete(otp_entry)
            db.session.commit()

            return {"message": "OTP verified successfully"}, 200

        except KeyError as e:
            return {"message": f"Missing key: {str(e)}"}, 400

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback any uncommitted changes
            return {"message": "Database error occurred", "error": str(e)}, 500

        except Exception as e:
            return {"message": "An unexpected error occurred", "error": str(e)}, 500


#  FORGOT PASSWORD

# send OTP
@sendotp_blueprint.route('/send-otp', methods=['POST'])
class SendOtp(Resource):
    def post(self):
        try:
            # Parse the JSON data from the request
            data = request.get_json()
            if not data:
                return {"message": "No input data provided"}, 400

            email = data.get('email')
            
            # Check if email is provided
            if not email:
                return {"message": "Please enter the email before submitting"}, 400
            
            # Validate email format
            if not re.match(email_regex, email):
                return {"message": "Invalid email format"}, 400
            
            # Check if the email is registered in the system
            user = Users.query.filter_by(email=email).first()
            if not user:
                return {"message": "Email not registered"}, 404

            # Generate OTP and set expiration time
            otp_code = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=5)

            # Check if there's an existing OTP entry for the email
            otp_entry = OTP.query.filter_by(email=email).first()
            if otp_entry:
                db.session.delete(otp_entry)
                db.session.commit()

            # Create a new OTP entry
            new_otp = OTP(email=email, otp=otp_code, expires_at=expires_at)
            db.session.add(new_otp)
            db.session.commit()

            # Send OTP via email
            email_status = self.send_email(email, otp_code)
            if email_status == "Email sent successfully!":
                return {"message": "OTP sent successfully"}, 200
            else:
                return {"message": "Failed to send email"}, 500

        except KeyError as e:
            return {"message": f"Missing key: {str(e)}"}, 400

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"message": "Database error occurred", "error": str(e)}, 500

        except Exception as e:
            return {"message": "An unexpected error occurred", "error": str(e)}, 500

    def send_email(self, email, otp_code):
        sender_email = "lsoneproject@gmail.com"
        app_password = "kpme ktaz mdhk nhyi"

        subject = "Your OTP Code for Password Reset"
        body = f"Your OTP code is: {otp_code}\nIt is valid for 5 minutes."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
                return "Email sent successfully!"
        except smtplib.SMTPAuthenticationError:
            return "SMTP Authentication Error: Invalid email credentials"
        
        except smtplib.SMTPConnectError:
            return "SMTP Connection Error: Unable to connect to email server"
        
        except smtplib.SMTPException as e:
            return f"SMTP Error: {str(e)}"
        
        except Exception as e:
            return f"General Email Error: {str(e)}"


# verify OTP
@sendotp_blueprint.route('/verify-otp', methods=['POST'])
class VerifyOtp(Resource):
    def post(self):
        try:
            # Get the input data
            data = request.json
            email = data.get('email')
            otp_code = data.get('otp')

            # Validate input
            if not email or not otp_code:
                return {"message": "Email and OTP are required"}, 400

            # Check for OTP entry in the database
            otp_entry = OTP.query.filter_by(email=email, otp=otp_code).first()

            # Handle case if OTP does not exist
            if not otp_entry:
                return {"message": "Invalid OTP"}, 400

            # Check if OTP has expired
            if otp_entry.expires_at < datetime.now():
                db.session.delete(otp_entry)
                db.session.commit()
                return {"message": "OTP has expired"}, 400

            # Delete OTP after successful verification
            db.session.delete(otp_entry)
            db.session.commit()

            return {"message": "OTP verified successfully"}, 200
        
        except SQLAlchemyError as e:
            # Rollback any changes and log the error
            db.session.rollback()
            return {"message": "Database error occurred", "error": str(e)}, 500
        
        except Exception as e:
            # Handle unexpected errors
            return {"message": "An error occurred", "error": str(e)}, 500


# reset PASSWORD
@sendotp_blueprint.route('/reset-password', methods=['POST'])
class ResetPassword(Resource):
    def post(self):
        try:
            # Get the input data
            data = request.json
            email = data.get('email')
            new_password = data.get('new_password')

            # Validate input
            if not new_password:
                return {"message": "Enter the Password before submitting"}, 400

            # Check if user exists
            user = Users.query.filter_by(email=email).first()

            # Handle case if user does not exist
            if not user:
                return {"message": "User not found"}, 404

            # Check if the new password is different from the old one
            if check_password_hash(user.users_pswd, new_password):
                return {"message": "Your new Password must be different from the old password"}, 400

            # Update the user's password
            user.users_pswd = generate_password_hash(new_password)
            db.session.commit()

            return {"message": "Password Reset successful"}, 200

        except SQLAlchemyError as e:
            # Handle database errors (e.g., issues with commit, session, etc.)
            db.session.rollback()
            return {"message": "Database error occurred", "error": str(e)}, 500

        except Exception as e:
            # Handle unexpected errors
            return {"message": "An error occurred", "error": str(e)}, 500
    