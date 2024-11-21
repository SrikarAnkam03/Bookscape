from flask import request, jsonify
from flask_restx import Resource
from app.main_app import db
from app.main_app.models.addresses import Addresses
from app.main_app.dto.addresses import AddressesDto
from flask_jwt_extended import jwt_required, get_jwt_identity

addressesapi_blueprint = AddressesDto.addressapi

# Add a new address
@addressesapi_blueprint.route('', methods=['POST'])
class AddAddress(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        # Extract fields from request data
        recipient_name = data.get('recipient_name', '').strip()
        address = data.get('address', '').strip()
        address_type = data.get('address_type', '').strip()

        # Validate all required fields
        if not recipient_name:
            return {'message': 'Recipient name is required'}, 400
        if len(recipient_name) > 100:
            return {'message': 'Recipient name must be less than 100 characters'}, 400

        if not address:
            return {'message': 'Address is required'}, 400
        if len(address) > 255:
            return {'message': 'Address must be less than 255 characters'}, 400

        if not address_type:
            return {'message': 'Address type is required'}, 400
        if address_type not in ['Home', 'Office', 'Other']:
            return {'message': "Address type must be 'Home', 'Office', or 'Other'"}, 400

        # Create new address entry
        new_address = Addresses(
            user_id=user_id,
            recipient_name=recipient_name,
            address=address,
            address_type=address_type
        )

        try:
            db.session.add(new_address)
            db.session.commit()
            return {'message': 'Address added successfully'}, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to add address. Error: {str(e)}'}, 500


# Update an existing address
@addressesapi_blueprint.route('', methods=['PUT'])
class UpdateAddress(Resource):
    @jwt_required()
    def put(self):
        data = request.json
        address_id = data.get('address_id')

        if not address_id:
            return {'message': 'Address ID is required'}, 400

        try:
            address = Addresses.query.get(address_id)
            if not address:
                return {'message': 'Address not found'}, 404

            address.recipient_name = data.get('recipient_name', address.recipient_name)
            address.address = data.get('address', address.address)
            address.address_type = data.get('address_type', address.address_type)

            db.session.commit()
            return {'message': 'Address updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to update address. Error: {str(e)}'}, 500


# Delete an address
@addressesapi_blueprint.route('', methods=['DELETE'])
class DeleteAddress(Resource):
    @jwt_required()
    def delete(self):
        address_id = request.args.get('address_id')
        if not address_id:
            return {'message': 'Address ID is required'}, 400

        try:
            address = Addresses.query.get(address_id)
            if not address:
                return {'message': 'Address not found'}, 404

            db.session.delete(address)
            db.session.commit()
            return {'message': 'Address deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Failed to delete address. Error: {str(e)}'}, 500


# Get all addresses for the logged-in user
@addressesapi_blueprint.route('', methods=['GET'])
class GetAddresses(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        if not user_id:
            return {'message': 'User ID is required'}, 400

        try:
            addresses = Addresses.query.filter_by(user_id=user_id).all()
            if not addresses:
                return {'message': 'No addresses found for this user'}, 200

            return [
                {
                    'address_id': str(addr.address_id),
                    'address': str(addr.address),
                    'recipient_name': str(addr.recipient_name),
                    'address_type': addr.address_type,
                } for addr in addresses
            ], 200
        except Exception as e:
            return {'message': f'Failed to retrieve addresses. Error: {str(e)}'}, 500
