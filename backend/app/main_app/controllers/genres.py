from app.main_app.dto.genres import GenresDto
from flask_restx import Resource
from flask import request, jsonify
from app.main_app import db
from app.main_app.models.genres import Genres
import uuid
from app.main_app.dto.users import UsersDto

genreapi_blueprint = GenresDto.genreapi


#genre
@genreapi_blueprint.route('', methods=['GET'])
class Getgenre(Resource):
    def get(self):
        try:
            # Query the Genres table to get all genres
            genres = Genres.query.all()

            if not genres:
                return {'message': 'No genres found'}, 404

            # Prepare the list of genres for the response
            genres_list = []
            for genre in genres:
                genres_list.append({
                    'genre_id': str(genre.genre_id),
                    'genre_name': genre.genre_name
                })

            return {'genres': genres_list}, 200

        except Exception as e:
            # Catch any exceptions and return an error message with a 500 status
            return {'message': f'An error occurred: {str(e)}'}, 500
