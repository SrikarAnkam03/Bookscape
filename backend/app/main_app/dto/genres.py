from flask_restx import Namespace

class GenresDto:
    genreapi = Namespace('genre',description='api to fetch genre')