from flask import Flask
from flask_restx import Api
import config
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.extensions import bcrypt
from app.models.user import User
from app.services.facade_instance import facade

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.api.v1.auth import api as auth_ns

jwt = JWTManager()

def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    existing_user = facade.user_repo.get_by_attribute('email', 'john2.doe@example.com')
    if existing_user:
        existing_user.hash_password("123456")
        facade.user_repo.update(existing_user.id, {})
        print("Mot de passe de l'utilisateur test mis à jour 🔹")
    else:
        facade.create_user({
            "first_name": "John",
            "last_name": "Doe",
            "email": "john2.doe@example.com",
            "password": "123456",
            "is_admin": True
        })
        print("Utilisateur test créé ✅")
    return app
