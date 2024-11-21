from flask import Blueprint
from flask_restx import Api
from app.main_app.controllers.users import (userapi_blueprint, updatedetailsapi_blueprint,loginapi_blueprint, signup_blueprint, getdetailsapi_blueprint, listusers_blueprint)
from app.main_app.controllers.seller import(deleteapi_blueprint, sellerapi_blueprint, sellers_blueprint)
from app.main_app.controllers.books import (book_blueprint, books_blueprint, sellerBooks_blueprint, adminSellerBooks_blueprint)
from app.main_app.controllers.genres import(genreapi_blueprint)
from app.main_app.controllers.authors import(authorsapi_blueprint)
from app.main_app.controllers.addresses import(addressesapi_blueprint)
from app.main_app.controllers.wishlist import(wishlist_blueprint, wishlist_items_blueprint)
from app.main_app.controllers.cart import (cart_blueprint, cart_items_blueprint)
from app.main_app.controllers.wallet import (wallet_blueprint)
from app.main_app.controllers.orders import (orders_blueprint)
from app.main_app.controllers.reviews import (review_blueprint)
from app.main_app.controllers.otp import (sendotp_blueprint, emailVerification_blueprint)


blueprint = Blueprint('api',__name__)
api = Api(blueprint, title='Bookscape')


api.add_namespace(loginapi_blueprint)
api.add_namespace(signup_blueprint)

api.add_namespace(sellerapi_blueprint)
api.add_namespace(sellers_blueprint)

api.add_namespace(updatedetailsapi_blueprint)
api.add_namespace(deleteapi_blueprint)
api.add_namespace(getdetailsapi_blueprint)
api.add_namespace(listusers_blueprint)

api.add_namespace(userapi_blueprint)

api.add_namespace(sellerBooks_blueprint)
api.add_namespace(book_blueprint)
api.add_namespace(books_blueprint)
api.add_namespace(genreapi_blueprint)
api.add_namespace(authorsapi_blueprint)
api.add_namespace(adminSellerBooks_blueprint)

api.add_namespace(addressesapi_blueprint)

api.add_namespace(wishlist_blueprint)
api.add_namespace(wishlist_items_blueprint)

api.add_namespace(cart_blueprint)
api.add_namespace(cart_items_blueprint)

api.add_namespace(wallet_blueprint)

api.add_namespace(orders_blueprint)

api.add_namespace(review_blueprint)

api.add_namespace(sendotp_blueprint)
api.add_namespace(emailVerification_blueprint)