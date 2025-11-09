from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.extensions import db, bcrypt, jwt
import config

def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API')

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    with app.app_context():
        from app.services.facade_instance import facade
        from app.models.user import User
        from app.models.amenity import Amenity
        from app.models.place_amenity import place_amenity
        from app.models.place import Place
        from app.models.review import Review
    
        db.create_all()

        existing_user = facade.user_repo.get_user_by_email('john2.doe@example.com')
        if not existing_user:
            try:
                facade.create_user({
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john2.doe@example.com",
                    "password": "123456",
                    "is_admin": True
                })
                print("Test user created")
            except Exception as e:
                print(f"Could not create test user: {e}")
    return app
