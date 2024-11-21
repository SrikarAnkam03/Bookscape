from flask_restx import Namespace, Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.main_app import db
from app.main_app.models.reviews import Reviews
from app.main_app.models.users import Users
from app.main_app.models.books import Books
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import SQLAlchemyError

review_blueprint = Namespace('reviews', description='Operations for reviews')

# Indian Time Zone Offset (UTC+5:30)
IST_OFFSET = timedelta(hours=5, minutes=30)

def get_indian_time(utc_time):
    """Convert UTC time to Indian Standard Time (IST)."""
    return utc_time + IST_OFFSET

# Add Review
@review_blueprint.route('/add', methods=['POST'])
class AddReview(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            book_id = data.get('book_id')
            rating = data.get('rating')

            if not user_id or not book_id or rating is None:
                return {'message': 'userId, book_id, and rating are required'}, 400

            book = Books.query.filter_by(book_id=book_id).first()
            if not book:
                return {'message': 'Book not found'}, 404

            new_review = Reviews(
                book_id=book_id,
                user_id=user_id,
                rating=rating,
                comment=data.get('comment'),
                created_at=datetime.utcnow()
            )
            db.session.add(new_review)
            db.session.commit()

            return {'message': 'Review added successfully'}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Database error occurred while adding review', 'error': str(e)}, 500

        except Exception as e:
            return {'message': 'An error occurred while adding review', 'error': str(e)}, 500


# Get Reviews of a Book
@review_blueprint.route('')
class GetReviews(Resource):
    @jwt_required()
    def get(self):
        try:
            book_id = request.args.get('book_id')

            if not book_id:
                return {'message': 'Book ID is required'}, 400

            reviews = Reviews.query.filter_by(book_id=book_id).all()

            if not reviews:
                return {'message': 'No reviews found for this book'}, 404

            user_ids = [review.user_id for review in reviews]
            users = {user.user_id: user.username for user in Users.query.filter(Users.user_id.in_(user_ids)).all()}

            reviews_list = [{
                'review_id': str(review.review_id),
                'username': users.get(review.user_id, 'Unknown User'),
                'rating': review.rating,
                'comment': review.comment,
                'created_at': time_ago(get_indian_time(review.created_at)),
            } for review in reviews]

            return {'reviews': reviews_list}, 200

        except SQLAlchemyError as e:
            return {'message': 'Database error occurred while retrieving reviews', 'error': str(e)}, 500

        except Exception as e:
            return {'message': 'An error occurred while retrieving reviews', 'error': str(e)}, 500


def time_ago(created_at):
    try:
        now = datetime.now(timezone.utc) + IST_OFFSET

        if created_at.tzinfo:
            created_at = created_at.replace(tzinfo=timezone.utc)
        diff = now - created_at
        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} secs ago"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{int(minutes)} mins ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{int(hours)} hrs ago"
        else:
            days = seconds // 86400
            return f"{int(days)} days ago"

    except Exception as e:
        return {'message': 'Error calculating time ago', 'error': str(e)}, 500


# Update Review
@review_blueprint.route('/<int:review_id>')
class UpdateReview(Resource):
    @jwt_required()
    def put(self, review_id):
        try:
            data = request.get_json()
            review = Reviews.query.filter_by(review_id=review_id, user_id=get_jwt_identity()).first()

            if not review:
                return {'message': 'Review not found or unauthorized'}, 404

            if 'rating' in data:
                review.rating = data['rating']

            if 'comment' in data:
                review.comment = data['comment']

            review.updated_at = datetime.utcnow()
            db.session.commit()

            return {'message': 'Review updated successfully'}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Database error occurred while updating review', 'error': str(e)}, 500

        except Exception as e:
            return {'message': 'An error occurred while updating review', 'error': str(e)}, 500


# Delete Review
@review_blueprint.route('/<int:review_id>')
class DeleteReview(Resource):
    @jwt_required()
    def delete(self, review_id):
        try:
            review = Reviews.query.filter_by(review_id=review_id, user_id=get_jwt_identity()).first()

            if not review:
                return {'message': 'Review not found or unauthorized'}, 404

            db.session.delete(review)
            db.session.commit()

            return {'message': 'Review deleted successfully'}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {'message': 'Database error occurred while deleting review', 'error': str(e)}, 500

        except Exception as e:
            return {'message': 'An error occurred while deleting review', 'error': str(e)}, 500
