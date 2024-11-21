from flask_restx import Namespace

class AddressesDto:
    addressapi = Namespace('address',description='api for address CRUD operations')