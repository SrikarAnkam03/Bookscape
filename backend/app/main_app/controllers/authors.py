from app.main_app.dto.authors import AuthorsDto
from app.main_app.models.authors import Authors
from flask_restx import Resource
from flask import request, jsonify
from app.main_app import db

authorsapi_blueprint = AuthorsDto.authorsapi

# Get author by name
@authorsapi_blueprint.route('', methods=['GET'])
class GetAuthor(Resource):
    def get(self):
        try:
            # Get the author name from the request JSON
            data = request.get_json()
            author_name = data.get('author_name', '').strip() if data else None

            if not author_name:
                return {'message': 'Please provide a proper author name'}, 400

            # Fetch the author from the database
            author = Authors.query.filter_by(author_name=author_name).first()

            if not author:
                return {'message': 'Author not found'}, 404

            # Prepare the author data for response
            author_data = {
                'author_id': author.author_id,
                'author_name': author.author_name,
                'bio': author.bio
            }
            return jsonify(author_data)

        except Exception as e:
            # Handle any unexpected errors
            return {'message': f'Failed to retrieve author. Error: {str(e)}'}, 500
