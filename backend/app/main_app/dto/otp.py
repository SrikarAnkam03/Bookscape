from flask_restx import Namespace 

class otpDto:
    otpapi = Namespace('otp', description='API for Forgot Password')
    emailVerifyOtpapi = Namespace('emailOtp', description='API for Email verifications')