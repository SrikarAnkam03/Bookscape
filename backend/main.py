from app.main_app import mydb
from flask_cors import CORS
from app import blueprint


backend = mydb()
CORS(backend)
backend.register_blueprint(blueprint)
backend.app_context().push()

if __name__ == "__main__":
    backend.run(debug=True)
