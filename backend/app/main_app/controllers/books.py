from flask_restx import Resource
from flask import request, jsonify
import sqlalchemy
from app.main_app import db
from datetime import datetime
from app.main_app.models.users import Users
from app.main_app.models.authors import Authors
from app.main_app.models.genres import Genres
from app.main_app.models.books import Books
from app.main_app.models.users import Users
from app.main_app.models.wishlist import Wishlist
from app.main_app.models.wishlist_items import WishlistItems
from app.main_app.dto.books import BooksDto
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

book_blueprint = BooksDto.bookapi
books_blueprint = BooksDto.booksapi
sellerBooks_blueprint = BooksDto.sellerbooksapi
adminSellerBooks_blueprint = BooksDto.adminSellerBoooksapi


UPLOAD_FOLDER = '/home/srikar/Desktop/bookscape-angular/bookscape/src/assets/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Add Book
@book_blueprint.route('', methods=['POST'])
class AddBook(Resource):
    @jwt_required()
    def post(self):
        try:
            if not request.form:
                return {'message': 'No form data provided'}, 400

            data = request.form

            # Check if file is present in the request
            if 'file' not in request.files:
                return {'message': 'File not found in the request'}, 400

            file = request.files['file']

            # Check if file is selected and valid
            if file.filename == '':
                return {'message': 'No file selected'}, 400
            if not allowed_file(file.filename):
                return {'message': 'File type not allowed'}, 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            try:
                file.save(file_path)
            except Exception as e:
                return {'message': f'Error saving file: {str(e)}'}, 500

            # Check if the book already exists based on the title
            existing_book = Books.query.filter_by(title=data.get('title')).first()
            if existing_book:
                return {'message': 'Book with this title already exists'}, 400

            # Handle author
            author_name = data.get('author_name')
            if not author_name:
                return {'message': 'Author name is required'}, 400
            author = Authors.query.filter_by(author_name=author_name).first()
            if not author:
                author = Authors(author_name=author_name)
                db.session.add(author)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return {'message': f'Error adding author: {str(e)}'}, 500

            # Handle genre
            genre_name = data.get('genre_name')
            if not genre_name:
                return {'message': 'Genre name is required'}, 400
            genre = Genres.query.filter_by(genre_name=genre_name).first()
            if not genre:
                genre = Genres(genre_name=genre_name)
                db.session.add(genre)
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return {'message': f'Error adding genre: {str(e)}'}, 500

            # Handle published date (if provided)
            published_date_str = data.get('published_date')
            try:
                published_date = datetime.strptime(published_date_str, '%Y-%m-%d').date() if published_date_str else datetime.now().date()
            except ValueError:
                return {'message': 'Invalid published date format. Use YYYY-MM-DD.'}, 400

            # Check if stock is within the allowed range (0 to 150)
            stock_value = int(data.get('stock', 0))
            if stock_value < 0 or stock_value > 150:
                return {'message': 'Stock must be between 0 and 150'}, 400

            # Create a new book
            new_book = Books(
                title=data.get('title'),
                author_id=author.author_id,
                genre_id=genre.genre_id,
                price=float(data.get('price', 0)),
                stock=stock_value,
                published_date=published_date,
                description=data.get('description', ''),
                cover_image_url=filename,
                isbn=data.get('isbn', ''),
                rating=float(data.get('rating', 0)),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                user_id=get_jwt_identity()
            )

            # Add the book to the database and commit
            db.session.add(new_book)
            db.session.commit()

            return {'message': 'Book created successfully'}, 201

        except sqlalchemy.exc.SQLAlchemyError as e:
            db.session.rollback()
            return {'message': f'Database error: {str(e)}'}, 500

        except FileNotFoundError as e:
            return {'message': f'File error: {str(e)}'}, 400

        except KeyError as e:
            return {'message': f'Missing data: {str(e)}'}, 400

        except AttributeError as e:
            return {'message': f'Attribute error: {str(e)}'}, 400

        except Exception as e:
            return {'message': f'Unexpected error: {str(e)}'}, 500


# Update Book
@book_blueprint.route('', methods=['PUT'])
class UpdateBook(Resource):
    @jwt_required()
    def put(self):
        try:
            data = request.get_json()

            # Check if the current title is provided
            current_title = data.get('currentTitle')
            if not current_title:
                return {'message': 'current_title is required'}, 400

            # Query the book based on the current title
            book = Books.query.filter_by(title=current_title).first()
            if not book:
                return {'message': 'Book not found'}, 404

            # Handle file upload for cover image
            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                if not allowed_file(file.filename):
                    return {'message': 'File type not allowed'}, 400

                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    file.save(file_path)
                except Exception as e:
                    return {'message': f'Error saving file: {str(e)}'}, 500
                book.cover_image_url = filename

            # Update book attributes based on the provided data
            if 'title' in data: 
                book.title = data['title']
            
            if 'author_name' in data:
                author = Authors.query.filter_by(author_name=data['author_name']).first()
                if not author:
                    author = Authors(author_name=data['author_name'])
                    db.session.add(author)
                    try:
                        db.session.commit()  # Commit after adding new author
                    except Exception as e:
                        db.session.rollback()
                        return {'message': f'Error adding author: {str(e)}'}, 500
                book.author_id = author.author_id

            if 'genre_name' in data:
                genre = Genres.query.filter_by(genre_name=data['genre_name']).first()
                if not genre:
                    genre = Genres(genre_name=data['genre_name'])
                    db.session.add(genre)
                    try:
                        db.session.commit()  # Commit after adding new genre
                    except Exception as e:
                        db.session.rollback()
                        return {'message': f'Error adding genre: {str(e)}'}, 500
                book.genre_id = genre.genre_id

            if 'price' in data: 
                book.price = data['price']

            if 'stock' in data: 
                stock_value = int(data['stock'])
                if stock_value < 0 or stock_value > 150:
                    return {'message': 'Stock must be between 0 and 150'}, 400
                book.stock = stock_value

            if 'description' in data: 
                book.description = data['description']

            if 'isbn' in data: 
                book.isbn = data['isbn']

            if 'rating' in data: 
                book.rating = data['rating']
                
            if 'published_date' in data:
                try:
                    book.published_date = datetime.strptime(data['published_date'], '%Y-%m-%d')
                except ValueError:
                    return {'message': 'Invalid published date format. Use YYYY-MM-DD.'}, 400

            # Commit all changes to the database
            db.session.commit()
            return {'message': 'Book updated successfully'}, 200

        except sqlalchemy.exc.SQLAlchemyError as e:
            # Handle database-specific errors
            db.session.rollback()
            return {'message': f'Database error: {str(e)}'}, 500

        except FileNotFoundError as e:
            # Handle file-related errors
            return {'message': f'File error: {str(e)}'}, 400

        except KeyError as e:
            # Handle missing keys in the request data
            return {'message': f'Missing data: {str(e)}'}, 400

        except AttributeError as e:
            # Handle unexpected attribute access errors
            return {'message': f'Attribute error: {str(e)}'}, 400

        except Exception as e:
            # Catch any other unexpected errors
            db.session.rollback()  # Rollback any pending changes in case of error
            return {'message': f'Unexpected error: {str(e)}'}, 500


# Delete Book
@book_blueprint.route('', methods=['DELETE'])
class DeleteBook(Resource):
    def delete(self):
        try:
            # Get data from the request body
            data = request.get_json()

            # Check if 'bookId' is present in the request data
            if not data or 'bookId' not in data:
                return {'message': 'Book Id is required'}, 400  # Bad Request

            # Query the book from the database using the book ID
            book = Books.query.filter_by(book_id=data['bookId']).first()

            # Check if the book exists
            if not book:
                return {'message': 'Book not found'}, 404  # Not Found

            # Mark the book as deleted
            book.is_delete = True
            book.display = False

            # Commit the changes to the database
            db.session.commit()

            return {'message': 'Book Deleted successfully'}, 200  # Success

        except sqlalchemy.exc.SQLAlchemyError as e:
            # Handle any database-related errors (e.g., query issues, commit failures)
            db.session.rollback()  # Rollback any uncommitted changes in case of an error
            return {'message': f'Database error: {str(e)}'}, 500  # Internal Server Error

        except AttributeError as e:
            # Handle missing attributes, e.g., if 'bookId' field is missing or invalid
            return {'message': f'Missing attribute error: {str(e)}'}, 400  # Bad Request

        except KeyError as e:
            # Handle any missing key in the request data, such as 'bookId' or other necessary data
            return {'message': f'Missing key in request data: {str(e)}'}, 400  # Bad Request

        except ValueError as e:
            # Handle any value-related errors, such as invalid types or incorrect format
            return {'message': f'Invalid value error: {str(e)}'}, 400  # Bad Request

        except Exception as e:
            # Handle any other unexpected errors
            db.session.rollback()  # Rollback any uncommitted changes in case of an error
            return {'message': f'Unexpected error: {str(e)}'}, 500  # Internal Server Error


# Get Book Details
@book_blueprint.route('', methods=['GET'])
class GetBookDetails(Resource):
    @jwt_required()
    def get(self):
        try:
            # Get the current user ID from the JWT token
            current_user_id = get_jwt_identity()

            # Retrieve book ID and title from the request arguments
            book_id = request.args.get('bookId')
            title = request.args.get('title')

            # Ensure that at least one of book_id or title is provided
            if not book_id and not title:
                return {'message': 'Book Id or title is required'}, 400  # Bad Request

            # Query the wishlist for the current user
            user_wishlist = Wishlist.query.filter_by(user_id=current_user_id).first()
            wishlist_id = user_wishlist.wishlist_id if user_wishlist else None

            # Prepare the query to fetch book details along with author and genre
            query = db.session.query(
                Books,
                Authors.author_name.label('author_name'),
                Genres.genre_name.label('genre_name')
            ).join(
                Authors, Books.author_id == Authors.author_id
            ).join(
                Genres, Books.genre_id == Genres.genre_id
            )

            # Apply filters based on book_id and title
            if book_id:
                query = query.filter(Books.book_id == book_id)
            if title:
                query = query.filter(Books.title.ilike(f'%{title}%'))  

            # Execute the query to fetch the book
            book = query.first()

            # Check if the book was found
            if not book:
                return {'message': 'Book not found'}, 404  # Not Found

            # Check if the book is in the user's wishlist
            is_favorited = False
            if wishlist_id:
                is_favorited = WishlistItems.query.filter_by(
                    wishlist_id=wishlist_id, book_id=book.Books.book_id
                ).first() is not None

            # Prepare the book details response
            book_details = {
                'book_id': str(book.Books.book_id),
                'title': book.Books.title,
                'author_name': book.author_name,
                'genre_name': book.genre_name,
                'price': float(book.Books.price),
                'stock': book.Books.stock,
                'published_date': book.Books.published_date.isoformat() if book.Books.published_date else None,
                'description': book.Books.description,
                'cover_image_url': book.Books.cover_image_url,
                'isbn': book.Books.isbn,
                'rating': float(book.Books.rating) if book.Books.rating else None,
                'created_at': book.Books.created_at.isoformat(),
                'updated_at': book.Books.updated_at.isoformat(),
                'user_id': str(book.Books.user_id),
                'favorited': is_favorited 
            }

            return jsonify(book_details)

        except AttributeError as e:
            # Handle missing attribute error (e.g., missing relationship or attribute)
            return {'message': f'Missing attribute in the request or database: {str(e)}'}, 400

        except ValueError as e:
            # Handle any value-related errors, such as invalid input values
            return {'message': f'Invalid value: {str(e)}'}, 400

        except sqlalchemy.exc.SQLAlchemyError as e:
            # Handle any SQLAlchemy database-related errors (query issues, connection errors)
            return {'message': f'Database error: {str(e)}'}, 500

        except Exception as e:
            # Catch all other unexpected errors
            return {'message': f'Unexpected error: {str(e)}'}, 500


# Fetch All Books
@books_blueprint.route('')
class BookList(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()

            user_wishlist = Wishlist.query.filter_by(user_id=user_id).first()
            wishlist_id = user_wishlist.wishlist_id if user_wishlist else None

            wishlist_book_ids = set(
                item.book_id for item in WishlistItems.query.filter_by(wishlist_id=wishlist_id).all()
            ) if wishlist_id else set()

            books = Books.query.filter(
                Books.display == True,
                Books.is_delete == False
            ).order_by(Books.created_at.desc()).all()

            books_list = [{
                'seller': book.user.username,
                'book_id': str(book.book_id),
                'title': book.title,
                'author_name': book.author.author_name,
                'genre_name': book.genre.genre_name,
                'price': float(book.price),
                'stock': str(book.stock),
                'published_date': book.published_date.strftime('%Y-%m-%d') if book.published_date else None,
                'cover_image_url': book.cover_image_url,
                'description': book.description,
                'isbn': book.isbn,
                'rating': float(book.rating) if book.rating else None,
                'is_favorited': book.book_id in wishlist_book_ids
            } for book in books]

            return jsonify(books_list)

        except Exception as e:
            return {'message': f'Unexpected error: {str(e)}'}, 500


# Fetch All Books of seller
@sellerBooks_blueprint.route('')
class SellerBooks(Resource):
    @jwt_required() 
    def get(self):
        try:
            # Retrieve the user ID from JWT token
            user_id = get_jwt_identity()

            # Query for the user based on the user_id
            user = Users.query.filter_by(user_id=user_id).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Query for books by the user, along with their author and genre details
            user_books = db.session.query(
                Books,
                Authors.author_name.label('author_name'),
                Genres.genre_name.label('genre_name')
            ).join(
                Authors, Books.author_id == Authors.author_id
            ).join(
                Genres, Books.genre_id == Genres.genre_id
            ).filter(
                Books.user_id == user.user_id,
                Books.is_delete == False
            ).order_by(Books.updated_at.desc()).all()

            if not user_books:
                return {'message': 'No books found for this user'}, 404

            # Prepare the list of books to return in the response
            books_list = []
            for book, author_name, genre_name in user_books:
                books_list.append({
                    'book_id': str(book.book_id),
                    'title': book.title,
                    'author_name': author_name, 
                    'genre_name': genre_name,    
                    'price': float(book.price),
                    'stock': book.stock,
                    'isbn': book.isbn,
                    'rating': float(book.rating),
                    'published_date': book.published_date.isoformat(),
                    'description': book.description,
                    'cover_image_url': book.cover_image_url,
                    'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S') if book.updated_at else None
                })

            return {'books': books_list}, 200

        except Exception as e:
            # Catch all exceptions and return a server error response
            return {'message': f'An error occurred: {str(e)}'}, 500


# Fetch Books of Sellers
@adminSellerBooks_blueprint.route('')
class AdminSellerBooks(Resource):
    def get(self):
        try:
            # Retrieve the 'username' from the query parameters
            username = request.args.get('username')
            
            # Query the Users table to find the user based on the username
            user = Users.query.filter_by(username=username).first()

            if not user:
                return {'message': 'User not found'}, 404

            # Query for books of the user, including author and genre information
            user_books = db.session.query(
                Books,
                Authors.author_name.label('author_name'),
                Genres.genre_name.label('genre_name')
            ).join(
                Authors, Books.author_id == Authors.author_id
            ).join(
                Genres, Books.genre_id == Genres.genre_id
            ).filter(
                Books.user_id == user.user_id,
                Books.is_delete == False  
            ).order_by(Books.updated_at.desc()).all()

            if not user_books:
                return {'message': 'No books found for this Seller'}, 404

            # Prepare the books list for the response
            books_list = []
            for book, author_name, genre_name in user_books:
                books_list.append({
                    'book_id': str(book.book_id),
                    'title': book.title,
                    'author_name': author_name, 
                    'genre_name': genre_name,    
                    'price': float(book.price),
                    'stock': book.stock,
                    'isbn': book.isbn,
                    'rating': float(book.rating),
                    'published_date': book.published_date.isoformat(),
                    'description': book.description,
                    'cover_image_url': book.cover_image_url,
                    'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S') if book.updated_at else None
                })

            return {'books': books_list}, 200

        except Exception as e:
            # Catch all exceptions and return a server error response
            return {'message': f'An error occurred: {str(e)}'}, 500
