from flask_restx import Resource
from flask import request
from app.main_app import db
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.main_app.models.authors import Authors
from app.main_app.models.wishlist import Wishlist
from app.main_app.models.users import Users
from app.main_app.models.roles import Roles
from app.main_app.models.wishlist_items import WishlistItems
from app.main_app.dto.wishlist import wishlistDto
from app.main_app.models.books import Books

wishlist_blueprint = wishlistDto.wishlistapi
wishlist_items_blueprint = wishlistDto.wishlist_itemsapi

# CREATE WISHLIST 
@wishlist_blueprint.route('', methods=['POST'])
class CreateWishlist(Resource):
    @jwt_required()
    def post(self):
        try:
            # Get user_id from JWT token
            user_id = get_jwt_identity()

            # Query the user from the Users table using the user_id
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Query the role of the user
            role = Roles.query.filter_by(role_id=user.role_id).first()

            if not role:
                return {'message': 'Role not found for the user'}, 404

            # If role is 'User', proceed to check wishlist
            if role.role == 'User':
                # Check if the user already has a wishlist
                wishlist = Wishlist.query.filter_by(user_id=user_id).first()

                if wishlist:
                    return {'message': 'Wishlist already exists for this user', 'wishlist_id': str(wishlist.wishlist_id)}, 200

                # Create a new wishlist if not found
                try:
                    new_wishlist = Wishlist(user_id=user_id)
                    db.session.add(new_wishlist)
                    db.session.commit()

                    return {'message': 'Wishlist created successfully', 'wishlist_id': str(new_wishlist.wishlist_id)}, 201

                except Exception as e:
                    # Rollback the session in case of any error
                    db.session.rollback()
                    print(f"Error: {str(e)}")  # Replace with proper logging in production
                    return {'message': f'An error occurred while creating the wishlist: {str(e)}'}, 500
            else:
                return {'message': 'Wishlist is not required for non-users'}, 200

        except Exception as e:
            # General exception handler for unexpected errors
            db.session.rollback()
            print(f"Error: {str(e)}")  # Replace with proper logging in production
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


# ADD ITEMS TO WISHLISTITEMS
@wishlist_items_blueprint.route('', methods=['POST'])
class AddToWishlist(Resource):
    def post(self):
        try:
            # Get the request data
            data = request.get_json()

            # Validate that wishlist_id and bookId are provided
            wishlist_id = data.get('wishlist_id')
            book_id = data.get('bookId')

            if not wishlist_id or not book_id:
                return {'message': 'Wishlist ID and Book ID are required'}, 400

            # Query the book from the Books table
            book = Books.query.filter_by(book_id=book_id).first()
            if not book:
                return {'message': 'Book not found'}, 404

            # Query the wishlist from the Wishlist table
            wishlist = Wishlist.query.filter_by(wishlist_id=wishlist_id).first()
            if not wishlist:
                return {'message': 'Wishlist not found. Please create a wishlist first.'}, 404

            # Check if the book is already in the wishlist
            wishlist_item = WishlistItems.query.filter_by(wishlist_id=wishlist_id, book_id=book_id).first()
            if wishlist_item:
                return {'message': 'Book already in the wishlist'}, 200

            # Create a new wishlist item
            new_wishlist_item = WishlistItems(
                wishlist_id=wishlist_id,
                book_id=book.book_id
            )

            # Add to session and commit
            db.session.add(new_wishlist_item)
            db.session.commit()

            return {'message': 'Book added to wishlist successfully'}, 201

        except Exception as e:
            # Catch any exception that occurs during the process
            db.session.rollback()  # Ensures the session is rolled back if an error occurs
            return {'message': f'An error occurred while adding the book to the wishlist: {str(e)}'}, 500


# DELETE FROM WISHLIST ITEMS
@wishlist_items_blueprint.route('', methods=['DELETE'])
class RemoveFromWishlist(Resource):
    def delete(self):
        try:
            # Get the request data
            data = request.get_json()

            # Check if the bookId is provided in the request
            book_id = data.get('bookId')

            if not book_id:
                return {'message': 'Book ID is required'}, 400  # Bad Request if no bookId is provided

            # Query the wishlist item from the WishlistItems table
            wishlist_item = WishlistItems.query.filter_by(book_id=book_id).first()

            if not wishlist_item:
                return {'message': 'Wishlist item not found'}, 404  # Not Found if the item is not in the wishlist

            # Delete the wishlist item from the database
            db.session.delete(wishlist_item)
            db.session.commit()

            # Return success message if item is removed successfully
            return {'message': 'Wishlist item removed successfully'}, 200  # Success message

        except Exception as e:
            # Catch any error that occurs during the execution of the function
            db.session.rollback()  # Ensure that the session is rolled back in case of any error
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500  # Internal Server Error for any other unexpected errors


# GET WISHLIST ITEMS
@wishlist_items_blueprint.route('/', methods=['GET'])
class GetWishlistItems(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get wishlist_id from query parameters
            wishlist_id = request.args.get('wishlist_id')

            if not wishlist_id:
                return {'message': 'Wishlist ID is required'}, 400  # Bad Request if no wishlist_id is provided

            # Query the wishlist items from the WishlistItems table
            wishlist_items = WishlistItems.query.filter_by(wishlist_id=wishlist_id).all()

            if not wishlist_items:
                return {'message': 'No items found in the wishlist'}, 200  # Return empty message if no items

            items = []
            for item in wishlist_items:
                # Query the book and author based on the wishlist item
                book = Books.query.get(item.book_id)
                if book:
                    author = Authors.query.get(book.author_id)
                    items.append({
                        'wishlist_item_id': str(item.wishlist_item_id),
                        'book_id': str(book.book_id),
                        'title': book.title,
                        'author': author.author_name if author else 'Unknown',  # Handle missing author gracefully
                        'display': book.display,
                        'rating': str(book.rating),
                        'price': str(book.price),
                        'stock': int(book.stock),
                        'cover_image_url': book.cover_image_url
                    })

            return {'wishlist_items': items}, 200  # Return the wishlist items as response

        except Exception as e:
            # Catch any unexpected error and return a server error response
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500

