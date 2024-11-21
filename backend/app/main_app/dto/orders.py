from flask_restx import Namespace 

class OrdersDto:
    ordersapi = Namespace('orders', description='API for orders')
