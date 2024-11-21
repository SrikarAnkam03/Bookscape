from flask_restx import Namespace 
 
class RolesDto:
    roleapi = Namespace('role',description='api for role related operations')