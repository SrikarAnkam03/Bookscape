from flask_restx import Namespace

class UsersDto:
    signupapi = Namespace('signup',description='api for user signup')
    loginapi = Namespace('login', description='api login')
    updatedetailsapi = Namespace('update', description='api to update user details')
    getdetailsapi = Namespace('user', description='api to show details of user')
    listusersapi = Namespace('users',description='api to get list of users')
    userapi = Namespace('', description='api for User endpoint')

    sellerapi = Namespace('seller', description='api for seller signup')
    sellersapi = Namespace ('sellers', description='api for fetching list of sellers')
    approveSellerapi = Namespace('approve', description='api for approving seller')
    deleteapi = Namespace('delete', description='api to delete user account')
