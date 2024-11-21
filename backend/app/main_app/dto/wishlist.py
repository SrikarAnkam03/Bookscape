from flask_restx import Namespace

class wishlistDto:
    wishlistapi = Namespace('wishlist',description = 'api to get wishlist details')
    wishlist_itemsapi = Namespace('wishlistItems',description='api to get wishlist items')