from flask_restx import Namespace

class BooksDto:
    bookapi = Namespace('book', description='Api for Books CRUD operations')
    booksapi = Namespace('books', description='Api for fetch all books')
    sellerbooksapi = Namespace('sellerBooks',description='Api to fetch all books of a seller')
    adminSellerBoooksapi = Namespace('adminSellerBooks',description='Api to fetch all books of a seller')