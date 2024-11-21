from flask_restx import Resource
from flask import request
from app.main_app import db
from app.main_app.dto.cart import CartDto
from app.main_app.models.cart import Cart
from app.main_app.models.users import Users
from app.main_app.models.roles import Roles
from app.main_app.models.books import Books
from app.main_app.models.authors import Authors
from app.main_app.models.cart_items import CartItems
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

cart_blueprint = CartDto.cartapi
cart_items_blueprint = CartDto.cart_itemsapi


@cart_blueprint.route('', methods=['POST'])
class CreateCart(Resource):
    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()

            if not user_id:
                return {'message': 'User ID is required'}, 400

            user = Users.query.filter_by(user_id=user_id).first()
            if not user:
                return {'message': 'User not found'}, 404

            role = Roles.query.filter_by(role_id=user.role_id).first()
            if role.role != 'User':
                return {'message': 'Cart is not required for this role'}, 200

            cart = Cart.query.filter_by(user_id=user_id).first()
            if cart:
                return {'message': 'Cart already exists', 'cart_id': str(cart.cart_id)}, 200

            new_cart = Cart(user_id=user_id)
            db.session.add(new_cart)
            db.session.commit()
            return {'message': 'Cart created successfully', 'cart_id': str(new_cart.cart_id)}, 201

        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


@cart_items_blueprint.route('', methods=['POST'])
class AddToCart(Resource):
    def post(self):
        try:
            data = request.get_json()
            cart_id = data.get('cart_id')
            book_id = data.get('bookId')
            quantity = data.get('quantity')

            if not cart_id or not book_id or not quantity:
                return {'message': 'cart_id, bookId, and quantity are required.'}, 400

            book = Books.query.filter_by(book_id=book_id).first()
            if not book:
                return {'message': 'Book not found'}, 404

            cart = Cart.query.filter_by(cart_id=cart_id).first()
            if not cart:
                return {'message': 'Cart not found. Please create a cart first.'}, 404

            cart_item = CartItems.query.filter_by(cart_id=cart_id, book_id=book_id).first()

            if cart_item:
                new_quantity = cart_item.quantity + quantity
                if new_quantity <= book.stock:
                    cart_item.quantity = new_quantity
                    cart_item.price = book.price * new_quantity
                    db.session.commit()
                    return {'message': f'{quantity} Book(s) have been added to your cart.'}, 200
                elif cart_item.quantity < book.stock:
                    cart_item.quantity = book.stock
                    cart_item.price = book.price * book.stock
                    db.session.commit()
                    return {'message': 'Books were added to reach the maximum stock.'}, 200
                else:
                    return {'message': f'You already have {book.stock} Book(s) in your cart, which is the maximum available stock.'}, 200
            else:
                if quantity > book.stock:
                    return {'message': f'Only {book.stock} Book(s) are available in stock. Cannot add {quantity} Book(s).'}, 400

                new_cart_item = CartItems(cart_id=cart_id, book_id=book_id, quantity=quantity, price=book.price * quantity)
                db.session.add(new_cart_item)
                db.session.commit()
                return {'message': 'Book added to cart successfully'}, 201

        except IntegrityError:
            db.session.rollback()
            return {'message': 'An error occurred while adding the book to the cart.'}, 500
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


@cart_items_blueprint.route('/<string:cart_item_id>', methods=['PUT'])
class UpdateCartItemQuantity(Resource):
    def put(self, cart_item_id):
        try:
            data = request.get_json()
            new_quantity = data.get('quantity')

            if new_quantity is None or new_quantity <= 0:
                return {'message': 'Quantity must be a positive integer'}, 400

            cart_item = CartItems.query.get(cart_item_id)
            if not cart_item:
                return {'message': 'Cart item not found'}, 404

            book = Books.query.get(cart_item.book_id)
            if not book:
                return {'message': 'Book not found'}, 404

            if new_quantity > book.stock:
                return {'message': f'Only {book.stock} items available in stock'}, 400

            cart_item.quantity = new_quantity
            cart_item.price = book.price * new_quantity
            db.session.commit()
            return {'message': 'Cart item quantity updated successfully'}, 200

        except IntegrityError:
            db.session.rollback()
            return {'message': 'An error occurred while updating the cart item quantity.'}, 500
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


@cart_items_blueprint.route('/<string:cart_item_id>', methods=['DELETE'])
class RemoveFromCart(Resource):
    def delete(self, cart_item_id):
        try:
            cart_item = CartItems.query.get(cart_item_id)
            if not cart_item:
                return {'message': 'Cart item not found'}, 404

            db.session.delete(cart_item)
            db.session.commit()
            return {'message': 'Cart item removed successfully'}, 200

        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500


@cart_items_blueprint.route('', methods=['GET'])
class GetCartItems(Resource):
    @jwt_required()
    def get(self):
        try:
            cart_id = request.args.get('cart_id')
            if not cart_id:
                return {'message': 'Cart ID is missing'}, 400

            cart = Cart.query.filter_by(cart_id=cart_id).first()
            if not cart:
                return {'message': 'User does not have a cart'}, 404

            cart_items = CartItems.query.filter_by(cart_id=cart.cart_id).order_by(CartItems.created_at.desc()).all()
            if not cart_items:
                return {'cart_items': []}, 200

            items = []
            for item in cart_items:
                book = Books.query.get(item.book_id)
                author = Authors.query.get(book.author_id) if book else None

                if book:
                    items.append({
                        'cart_item_id': str(item.cart_item_id),
                        'book_id': str(book.book_id),
                        'title': book.title,
                        'display': book.display,
                        'author_name': author.author_name if author else None,
                        'cover_image_url': book.cover_image_url,
                        'stock': int(book.stock),
                        'quantity': item.quantity,
                        'price': str(item.price)
                    })

            return {'cart_items': items}, 200

        except Exception as e:
            return {'message': str(e)}, 500
