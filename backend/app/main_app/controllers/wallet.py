from decimal import Decimal, InvalidOperation
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Resource
from app.main_app import db
from app.main_app.models.wallet import Wallet
from app.main_app.models.transactions import Transaction
from app.main_app.dto.wallet import walletDto

wallet_blueprint = walletDto.walletapi

# CREATE WALLET
@wallet_blueprint.route('', methods=['POST'])
class CreateWallet(Resource):
    @jwt_required()
    def post(self):
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()

            # Check if the user ID is not found
            if not user_id:
                return {'message': 'User ID is required'}, 400

            # Check if the wallet already exists for the user
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if wallet:
                return {'message': 'Wallet already exists'}, 200

            # Create a new wallet for the user
            new_wallet = Wallet(user_id=user_id)
            db.session.add(new_wallet)
            db.session.commit()

            # Return the newly created wallet details
            return {
                'wallet_id': str(new_wallet.wallet_id),
                'balance': str(new_wallet.balance)
            }, 201

        except Exception as e:
            # Rollback the session in case of any exception
            db.session.rollback()

            # Handle any unexpected errors (e.g., database connection issues, integrity errors)
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500
    

# FETCH WALLET BALANCE OF THE USER
@wallet_blueprint.route('/balance', methods=['GET'])
class GetWallet(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the user ID from the JWT token
            user_id = get_jwt_identity()

            # Query the wallet associated with the user ID
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            
            # If the wallet is not found, return an error
            if wallet is None:
                return {'message': 'Wallet not found'}, 404

            # Return the wallet details if found
            return {
                'wallet_id': str(wallet.wallet_id),
                'balance': str(wallet.balance)
            }, 200

        except Exception as e:
            # Rollback the session in case of any database-related or unexpected errors
            db.session.rollback()

            # Return a generic error message with the exception details for debugging
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500

    
# DEPOSIT MONEY INTO THE WALLET
@wallet_blueprint.route('/deposit', methods=['POST'])
class DepositWallet(Resource):
    def post(self):
        try:
            # Parse incoming request data
            data = request.get_json()
            user_id = data.get('userId')
            amount = data.get('amount')

            # Check for missing parameters
            if not user_id or amount is None:
                return {'message': 'User ID and amount are required'}, 400

            # Try to convert the amount to a Decimal
            try:
                amount = Decimal(amount)
            except (ValueError, InvalidOperation):
                return {'message': 'Invalid amount provided'}, 400
            
            # Check if the amount is greater than zero
            if amount <= 0:
                return {'message': 'Amount must be greater than zero'}, 400

            # Query for the wallet by user_id
            wallet = Wallet.query.filter_by(user_id=user_id).first()

            # Check if the wallet exists
            if wallet is None:
                return {'message': 'Wallet not found'}, 404

            # Update the wallet balance
            wallet.balance += amount

            # Create a transaction record
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=amount,
                transaction_type='credit'
            )
            db.session.add(transaction)

            # Commit the changes to the database
            db.session.commit()

            # Return success response with the updated balance
            return {'message': 'Deposit successful', 'balance': str(wallet.balance)}, 200

        except Exception as e:
            # Rollback the session in case of any error
            db.session.rollback()

            # Log the exception (for debugging purposes)
            print(f"Error: {str(e)}")  # This can be replaced by a proper logger

            # Return a generic error message
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# WITHDRAW MONEY FROM THE WALLET
@wallet_blueprint.route('/withdraw', methods=['POST'])
class WithdrawWallet(Resource):
    def post(self):
        try:
            # Parse incoming request data
            data = request.get_json()
            user_id = data.get('userId')
            amount = data.get('amount')

            # Validate presence of required fields
            if not user_id or amount is None:
                return {'message': 'User ID and amount are required'}, 400

            # Try to convert the amount to a Decimal
            try:
                amount = Decimal(amount)
            except (ValueError, InvalidOperation):
                return {'message': 'Invalid amount provided'}, 400
            
            # Check if the amount is greater than zero
            if amount <= 0:
                return {'message': 'Amount must be greater than zero'}, 400

            # Query for the wallet by user_id
            wallet = Wallet.query.filter_by(user_id=user_id).first()

            # Check if the wallet exists
            if wallet is None:
                return {'message': 'Wallet not found'}, 404

            # Check if there is sufficient balance
            if wallet.balance < amount:
                return {'message': 'Insufficient balance'}, 400

            # Update the wallet balance
            wallet.balance -= amount

            # Create a transaction record
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=amount,
                transaction_type='debit'
            )
            db.session.add(transaction)

            # Commit the changes to the database
            db.session.commit()

            # Return success response with the updated balance
            return {'message': 'Withdrawal successful', 'balance': str(wallet.balance)}, 200

        except Exception as e:
            # Rollback the session in case of any error
            db.session.rollback()

            # Log the exception (for debugging purposes)
            print(f"Error: {str(e)}")  # This can be replaced by a proper logger

            # Return a generic error message
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# FETCH TRANSACTIONS USER
@wallet_blueprint.route('/transactions', methods=['GET'])
class FetchUserTransactions(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the user_id from the JWT token
            user_id = get_jwt_identity()

            # Query the wallet for the user_id
            wallet = Wallet.query.filter_by(user_id=user_id).first()

            # If the wallet doesn't exist, return a 404 error
            if not wallet:
                return {'message': 'Wallet not found for the user'}, 404

            # Fetch the transactions for the wallet, ordered by the most recent
            transactions = Transaction.query.filter_by(wallet_id=wallet.wallet_id).order_by(Transaction.created_at.desc()).all()

            # Prepare the list of transactions
            transactions_list = []
            for transaction in transactions:
                transactions_list.append({
                    'transaction_id': str(transaction.transaction_id),
                    'amount': str(transaction.amount),
                    'transaction_type': transaction.transaction_type,
                    'created_at': transaction.created_at.isoformat(),
                })

            # Return the wallet ID and the list of transactions
            return {
                'wallet_id': str(wallet.wallet_id),
                'transactions': transactions_list
            }, 200

        except Exception as e:
            # Rollback the session in case of any error
            db.session.rollback()

            # Log the exception (for debugging purposes)
            print(f"Error: {str(e)}")  # Replace with proper logging in production

            # Return a generic error message
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500
