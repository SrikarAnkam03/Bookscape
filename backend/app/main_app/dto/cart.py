from flask_restx import Namespace 

class CartDto:
    cartapi = Namespace('cart', description='API for cart')
    cart_itemsapi = Namespace('cartItems', description='API for cart_items')