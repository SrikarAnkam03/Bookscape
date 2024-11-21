from flask_restx import Namespace

class AuthorsDto:
    authorsapi = Namespace('author',description='api to get author details')