from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main_app.models.transactions import Transaction
from app.main_app.models.order_items import OrderItems
from app.main_app.models.cart_items import CartItems
from app.main_app.models.addresses import Addresses
from app.main_app.models.authors import Authors
from app.main_app.models.orders import Orders
from app.main_app.models.wallet import Wallet
from app.main_app.models.books import Books
from app.main_app.models.users import Users
from app.main_app.models.cart import Cart
from app.main_app.dto.orders import OrdersDto
from sqlalchemy.exc import SQLAlchemyError
from flask_restx import Resource
from datetime import datetime
from app.main_app import db
from flask import request

orders_blueprint = OrdersDto.ordersapi

# TO PLACE ORDER
@orders_blueprint.route('', methods=['POST'])
class PlaceOrder(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            data = request.get_json()

            if not data:
                return {'message': 'Invalid input. Request body is missing'}, 400

            address_id = data.get('address_id')
            if not address_id:
                return {'message': 'Address ID is required'}, 400

            # Fetch the user's cart
            cart = Cart.query.filter_by(user_id=user_id).first()
            if not cart:
                return {'message': 'No items in cart to order'}, 400

            # Fetch all cart items
            cart_items = CartItems.query.filter_by(cart_id=cart.cart_id).all()
            if not cart_items:
                return {'message': 'No items in cart to order'}, 400

            # Get book details from the cart
            book_ids = [item.book_id for item in cart_items]
            books = Books.query.filter(Books.book_id.in_(book_ids)).all()
            book_map = {book.book_id: book for book in books}

            # Check if all books exist
            if not book_map:
                return {'message': 'Books not found in the database'}, 400

            # Check for out-of-stock items or items where quantity > stock
            out_of_stock_items = []
            over_quantity_items = []

            for item in cart_items:
                book = book_map.get(item.book_id)
                if not book:
                    continue  # Skip if the book is not found

                # Check if the book is out of stock
                if book.stock == 0:
                    out_of_stock_items.append(book.title)
                elif item.quantity > book.stock:
                    over_quantity_items.append({
                        'title': book.title,
                        'available_stock': book.stock,
                        'requested_quantity': item.quantity
                    })

            # Return appropriate error messages
            if out_of_stock_items:
                return {
                    'message': 'Order cannot be placed. The following items are out of stock',
                    'out_of_stock_items': out_of_stock_items
                }, 400

            if over_quantity_items:
                return {
                    'message': 'Order cannot be placed due to insufficient stock for some items',
                    'over_quantity_items': over_quantity_items
                }, 400

            # Calculate total amount
            total_amount = sum(item.price * item.quantity for item in cart_items)

            # Check buyer's wallet balance
            buyer_wallet = Wallet.query.filter_by(user_id=user_id).first()
            if not buyer_wallet:
                return {'message': 'Buyer wallet not found'}, 404

            if buyer_wallet.balance < total_amount:
                return {'message': 'Insufficient wallet balance'}, 400

            # Deduct balance from buyer's wallet and record transaction
            buyer_wallet.balance -= total_amount
            buyer_transaction = Transaction(
                wallet_id=buyer_wallet.wallet_id,
                amount=total_amount,
                transaction_type='debit'
            )
            db.session.add(buyer_transaction)

            # Create a new order
            new_order = Orders(user_id=user_id, address_id=address_id, total_amount=total_amount)
            db.session.add(new_order)
            db.session.flush()

            # Process each cart item and update stock
            for item in cart_items:
                book = book_map.get(item.book_id)
                if not book:
                    continue  # Skip if the book is not found

                # Check stock again to ensure availability
                if book.stock < item.quantity:
                    return {
                        'message': f'Book "{book.title}" is out of stock or insufficient stock available'
                    }, 400

                book.stock -= item.quantity

                # Credit seller's wallet
                seller_wallet = Wallet.query.filter_by(user_id=book.user_id).first()
                if not seller_wallet:
                    return {'message': f'Seller wallet not found for book "{book.title}"'}, 404

                seller_wallet.balance += item.price * item.quantity
                seller_transaction = Transaction(
                    wallet_id=seller_wallet.wallet_id,
                    amount=item.price * item.quantity,
                    transaction_type='credit'
                )
                db.session.add(seller_transaction)

                # Create OrderItems record
                order_item = OrderItems(
                    order_id=new_order.order_id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    price=item.price
                )
                db.session.add(order_item)

                # Remove item from cart
                db.session.delete(item)

            # Commit all changes to the database
            db.session.commit()

            return {
                'message': 'Order placed successfully',
                'order_id': str(new_order.order_id),
                'total_amount': float(new_order.total_amount)
            }, 201

        except KeyError as e:
            db.session.rollback()
            return {'message': f'Missing required data: {str(e)}'}, 400

        except ValueError as e:
            db.session.rollback()
            return {'message': f'Invalid data provided: {str(e)}'}, 400

        except AttributeError as e:
            db.session.rollback()
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'A database error occurred', 'error': str(e)}, 500

        except Exception as e:
            db.session.rollback()
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500


# TO GET ALL ORDERS OF SINGLE USER
@orders_blueprint.route('', methods=['GET'])
class GetUserOrders(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the user ID from JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'Not a valid user id'}, 400

            # Fetch all orders for the user, sorted by order date in descending order
            orders = Orders.query.filter_by(user_id=user_id).order_by(Orders.order_date.desc()).all()
            
            if not orders:
                return {'message': 'No orders found for this user'}, 404
            
            order_list = []

            for order in orders:
                try:
                    # Fetch address for each order
                    address = Addresses.query.filter_by(address_id=order.address_id).first()
                    if not address:
                        return {'message': f'Address not found for order ID {order.order_id}'}, 404

                    # Fetch all items associated with the current order
                    order_items = OrderItems.query.filter_by(order_id=order.order_id).all()

                    items_list = []
                    for item in order_items:
                        try:
                            # Fetch book details
                            book = Books.query.filter_by(book_id=item.book_id).first()
                            if not book:
                                return {'message': f'Book not found for book ID {item.book_id}'}, 404

                            # Fetch author details for the book
                            author = Authors.query.filter_by(author_id=book.author_id).first()
                            if not author:
                                return {'message': f'Author not found for author ID {book.author_id}'}, 404

                            # Prepare item details
                            items_list.append({
                                'order_item_id': str(item.order_item_id),
                                'book_id': str(item.book_id),
                                'title': book.title,
                                'image': book.cover_image_url,
                                'display': book.display,
                                'author_name': author.author_name,
                                'quantity': int(item.quantity),
                                'price': float(item.price)
                            })
                        except AttributeError as e:
                            return {'message': f'Error accessing book/author details: {str(e)}'}, 400
                        except Exception as e:
                            return {'message': 'An unexpected error occurred while fetching order items', 'error': str(e)}, 500

                    # Prepare order details
                    order_list.append({
                        'order_id': str(order.order_id),
                        'address': address.address,
                        'display': str(book.display),
                        'total_amount': float(order.total_amount),
                        'order_date': str(order.order_date),
                        'items': items_list
                    })
                
                except AttributeError as e:
                    return {'message': f'Error accessing address details for order ID {order.order_id}: {str(e)}'}, 400
                except Exception as e:
                    return {'message': 'An unexpected error occurred while fetching order details', 'error': str(e)}, 500

            return {'orders': order_list}, 200

        except KeyError as e:
            return {'message': f'Missing required data: {str(e)}'}, 400

        except ValueError as e:
            return {'message': f'Invalid data provided: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            # Handle any database-related errors
            return {'message': 'A database error occurred', 'error': str(e)}, 500

        except Exception as e:
            # Handle any other unexpected errors
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500

    
# TO GET ALL ORDERS OF SINGLE SELLER
@orders_blueprint.route('/seller', methods=['GET'])
class GetSellerOrders(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the seller (user) ID from the JWT token
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'Not a valid user ID'}, 400

            # Fetch all books associated with the seller
            books = Books.query.filter_by(user_id=user_id).all()
            if not books:
                return {'message': 'No books found for this seller'}, 404
            
            # Extract book IDs from the fetched books
            book_ids = [book.book_id for book in books]

            # Fetch order items related to the seller's books
            order_items = OrderItems.query.filter(OrderItems.book_id.in_(book_ids)).all()
            if not order_items:
                return {'message': 'No orders found for this seller'}, 404

            # Extract unique order IDs from order items
            order_ids = {item.order_id for item in order_items}

            # Fetch orders using the extracted order IDs, ordered by order date
            orders = Orders.query.filter(Orders.order_id.in_(order_ids)).order_by(Orders.order_date.desc()).all()
            if not orders:
                return {'message': 'No orders found for this seller'}, 404

            order_list = []

            for order in orders:
                try:
                    # Fetch the address for each order
                    address = Addresses.query.filter_by(address_id=order.address_id).first()
                    if not address:
                        return {'message': f'Address not found for order {order.order_id}'}, 404

                    # Filter order items specific to the current order
                    items_list = [item for item in order_items if item.order_id == order.order_id]
                    
                    formatted_items_list = []
                    for item in items_list:
                        try:
                            # Fetch book details for each order item
                            book = Books.query.filter_by(book_id=item.book_id).first()
                            if not book:
                                return {'message': f'Book not found for book_id {item.book_id}'}, 404

                            # Fetch author details for each book
                            author = Authors.query.filter_by(author_id=book.author_id).first()
                            if not author:
                                return {'message': f'Author not found for author_id {book.author_id}'}, 404

                            # Prepare the item details
                            formatted_items_list.append({
                                'order_item_id': str(item.order_item_id),
                                'book_id': str(item.book_id),
                                'title': book.title,
                                'image': book.cover_image_url,
                                'display': book.display,
                                'author_name': author.author_name,
                                'quantity': int(item.quantity),
                                'price': float(item.price)
                            })
                        except AttributeError as e:
                            return {'message': f'Error accessing book/author details: {str(e)}'}, 400
                        except Exception as e:
                            return {'message': 'An unexpected error occurred while fetching order items', 'error': str(e)}, 500

                    # Prepare the order details
                    order_list.append({
                        'order_id': str(order.order_id),
                        'address': address.address,
                        'total_amount': float(order.total_amount),
                        'order_date': str(order.order_date),
                        'items': formatted_items_list
                    })
                
                except AttributeError as e:
                    return {'message': f'Error accessing address details for order {order.order_id}: {str(e)}'}, 400
                except Exception as e:
                    return {'message': 'An unexpected error occurred while fetching order details', 'error': str(e)}, 500

            return {'orders': order_list}, 200

        except KeyError as e:
            return {'message': f'Missing required data: {str(e)}'}, 400

        except ValueError as e:
            return {'message': f'Invalid data provided: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            # Handle any database-related errors
            return {'message': 'A database error occurred', 'error': str(e)}, 500

        except Exception as e:
            # Handle any other unexpected errors
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500

    
# TO GET ORDER DETAILS OF A USER
@orders_blueprint.route('/details', methods=['GET'])
class GetOrderDetails(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the JSON data from the request
            data = request.get_json()
            
            if not data:
                return {'message': 'No input data provided'}, 400
            
            # Validate the presence of 'order_id' and 'order_item_id' in the request data
            if 'order_id' not in data or 'order_item_id' not in data:
                return {'message': 'Missing order_id or order_item_id in request'}, 400

            # Fetch the order based on the provided 'order_id'
            order = Orders.query.filter_by(order_id=data['order_id']).first()
            if not order:
                return {'message': 'Order not found'}, 404

            # Fetch the order item based on the provided 'order_item_id'
            orderItem = OrderItems.query.filter_by(order_item_id=data['order_item_id']).first()
            if not orderItem:
                return {'message': 'Order item not found'}, 404

            # Fetch the book details associated with the order item
            book = Books.query.get(orderItem.book_id)
            if not book:
                return {'message': 'Book not found for the given order item'}, 404

            # Fetch the address details associated with the order
            address = Addresses.query.get(order.address_id)
            if not address:
                return {'message': 'Address not found for the given order'}, 404

            # Prepare the order item details
            orderItem_details = {
                'book_title': book.title,
                'quantity': int(orderItem.quantity),
                'price': float(orderItem.price),
                'address': address.address,
                'order_date': str(order.order_date)
            }

            return {'order': orderItem_details}, 200
        
        # Handle specific exceptions
        except KeyError as e:
            return {'message': f'Missing key: {str(e)}'}, 400
        
        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400
        
        except SQLAlchemyError as e:
            # Handles all SQLAlchemy related errors (import from sqlalchemy.exc)
            return {'message': 'Database error occurred', 'error': str(e)}, 500
        
        except Exception as e:
            # Catch any other unexpected exceptions
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500


# TO GET ORDERS OF A SELLER
@orders_blueprint.route('/sold_books', methods=['GET'])
class GetSoldBooks(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the current user's ID from the JWT token
            user_id = get_jwt_identity()
            
            # Check if the user exists
            seller = Users.query.filter_by(user_id=user_id).first()
            if not seller:
                return {'message': 'User is not authorized to view sold books'}, 403

            # Query to find sold books by the seller
            sold_books = OrderItems.query \
                .join(Books, OrderItems.book_id == Books.book_id) \
                .filter(Books.user_id == user_id).all()
            
            if not sold_books:
                return {'message': 'No sold books found for this seller'}, 404

            sold_books_list = []
            total_earnings = 0

            # Loop through each sold book entry
            for sold_book in sold_books:
                book = Books.query.get(sold_book.book_id)
                
                # Check if the book exists
                if not book:
                    return {'message': f'Book not found for book_id {sold_book.book_id}'}, 404
                
                # Calculate total revenue for each sold book
                total_revenue = sold_book.price * sold_book.quantity
                total_earnings += total_revenue
                
                # Prepare the data for each sold book
                sold_books_list.append({
                    'book_id': str(book.book_id),
                    'title': book.title,
                    'quantity_sold': int(sold_book.quantity),
                    'price_per_unit': float(sold_book.price),
                    'total_revenue': float(total_revenue),
                    'order_date': str(sold_book.order.order_date) if sold_book.order else 'N/A'
                })

            # Return the response with the sold books data and total earnings
            return {
                'sold_books': sold_books_list,
                'total_earnings': float(total_earnings)
            }, 200

        # Handle specific exceptions
        except KeyError as e:
            return {'message': f'Missing key: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            # Handles all SQLAlchemy related errors
            return {'message': 'Database error occurred', 'error': str(e)}, 500

        except Exception as e:
            # Catch any other unexpected exceptions
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500


# TO GET ALL ORDERS 
@orders_blueprint.route('/admin', methods=['GET'])  
class GetAllOrders(Resource):
    @jwt_required()
    def get(self):
        try:
            # Fetch all orders sorted by the most recent order date
            orders = Orders.query.order_by(Orders.order_date.desc()).all()
            
            if not orders:
                return {'message': 'No orders found'}, 404

            order_list = []

            for order in orders:
                # Fetch the address for each order
                address = Addresses.query.filter_by(address_id=order.address_id).first()
                if not address:
                    return {'message': f'Address not found for order {order.order_id}'}, 404

                # Fetch the user associated with the order
                user = Users.query.filter_by(user_id=order.user_id).first()
                if not user:
                    return {'message': f'User not found for user_id {order.user_id}'}, 404

                # Fetch all items for the current order
                order_items = OrderItems.query.filter_by(order_id=order.order_id).all()
                items_list = []

                for item in order_items:
                    # Fetch the book associated with each order item
                    book = Books.query.filter_by(book_id=item.book_id).first()
                    if not book:
                        return {'message': f'Book not found for book_id {item.book_id}'}, 404

                    # Fetch the author of the book
                    author = Authors.query.filter_by(author_id=book.author_id).first()
                    if not author:
                        return {'message': f'Author not found for author_id {book.author_id}'}, 404

                    # Append each item details to the items_list
                    items_list.append({
                        'order_item_id': str(item.order_item_id),
                        'order_id':str(item.order_id),
                        'book_id': str(item.book_id),
                        'title': book.title,
                        'image': book.cover_image_url,
                        'author_name': author.author_name,
                        'quantity': int(item.quantity),
                        'price': float(item.price)
                    })

                # Append order details to the order_list
                order_list.append({
                    'order_id': str(order.order_id),
                    'username': user.username,
                    'address': address.address,
                    'total_amount': float(order.total_amount),
                    'order_date': str(order.order_date),
                    'items': items_list
                })

            return {'orders': order_list}, 200

        # Handle specific exceptions
        except KeyError as e:
            return {'message': f'Missing key: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            # Handles all SQLAlchemy related errors
            return {'message': 'Database error occurred', 'error': str(e)}, 500

        except Exception as e:
            # Catch any other unexpected exceptions
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500


# TO FETCH ORDER ITEMS FROM SINGLE ORDER
@orders_blueprint.route('/admin/<string:order_id>', methods=['GET'])
class GetOrderById(Resource):
    @jwt_required()
    def get(self, order_id):
        try:
            # Fetch the order by order_id
            order = Orders.query.filter_by(order_id=order_id).first()
            if not order:
                return {'message': f'Order with ID {order_id} not found'}, 404

            # Fetch the address for the order
            address = Addresses.query.filter_by(address_id=order.address_id).first()
            if not address:
                return {'message': f'Address not found for order {order_id}'}, 404

            # Fetch the user associated with the order
            user = Users.query.filter_by(user_id=order.user_id).first()
            if not user:
                return {'message': f'User not found for user_id {order.user_id}'}, 404

            # Fetch all items for the specified order
            order_items = OrderItems.query.filter_by(order_id=order_id).all()
            if not order_items:
                return {'message': f'No items found for order {order_id}'}, 404

            items_list = []

            for item in order_items:
                # Fetch the book associated with each order item
                book = Books.query.filter_by(book_id=item.book_id).first()
                if not book:
                    return {'message': f'Book not found for book_id {item.book_id}'}, 404

                # Fetch the author of the book
                author = Authors.query.filter_by(author_id=book.author_id).first()
                if not author:
                    return {'message': f'Author not found for author_id {book.author_id}'}, 404

                # Append each item details to the items_list
                items_list.append({
                    'order_item_id': str(item.order_item_id),
                    'order_id': str(item.order_id),
                    'book_id': str(item.book_id),
                    'title': book.title,
                    'image': book.cover_image_url,
                    'author_name': author.author_name,
                    'quantity': int(item.quantity),
                    'price': float(item.price)
                })

            # Construct the response with order details and items
            order_details = {
                'order_id': str(order.order_id),
                'username': user.username,
                'address': address.address,
                'total_amount': float(order.total_amount),
                'order_date': str(order.order_date),
                'items': items_list
            }

            return {'order': order_details}, 200

        # Handle specific exceptions
        except KeyError as e:
            return {'message': f'Missing key: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except SQLAlchemyError as e:
            # Handles all SQLAlchemy related errors
            return {'message': 'Database error occurred', 'error': str(e)}, 500

        except Exception as e:
            # Catch any other unexpected exceptions
            return {'message': 'An unexpected error occurred', 'error': str(e)}, 500
