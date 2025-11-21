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

        # Créer l'utilisateur de test
        existing_user = facade.user_repo.get_user_by_email('john2.doe@example.com')
        if not existing_user:
            try:
                existing_user = facade.create_user({
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john2.doe@example.com",
                    "password": "123456",
                    "is_admin": True
                })
                print("Test user created")
            except Exception as e:
                print(f"Could not create test user: {e}")
        
        # Créer des amenities de test
        existing_amenities = facade.amenity_repo.get_all()
        wifi = None
        pool = None
        parking = None
        ac = None
        kitchen = None
        tv = None
        
        if len(existing_amenities) == 0:
            try:
                wifi = facade.create_amenity({"name": "WiFi"})
                pool = facade.create_amenity({"name": "Swimming Pool"})
                parking = facade.create_amenity({"name": "Parking"})
                ac = facade.create_amenity({"name": "Air Conditioning"})
                kitchen = facade.create_amenity({"name": "Kitchen"})
                tv = facade.create_amenity({"name": "TV"})
                
                print("Test amenities created: 6 amenities")
            except Exception as e:
                print(f"Could not create amenities: {e}")
        else:
            # Récupérer les amenities existantes
            for amenity in existing_amenities:
                if amenity.name == "WiFi":
                    wifi = amenity
                elif amenity.name == "Swimming Pool":
                    pool = amenity
                elif amenity.name == "Parking":
                    parking = amenity
                elif amenity.name == "Air Conditioning":
                    ac = amenity
                elif amenity.name == "Kitchen":
                    kitchen = amenity
                elif amenity.name == "TV":
                    tv = amenity

        # Créer des lieux de test avec amenities
        existing_places = facade.place_repo.get_all()
        if len(existing_places) == 0 and existing_user:
            try:
                # Lieu 1 : Luxury Villa (avec piscine, AC, TV, WiFi)
                place1 = facade.create_place({
                    "title": "Luxury Villa",
                    "description": "Beautiful villa with ocean view and private pool",
                    "price": 150.0,
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "owner_id": existing_user.id
                })
                
                # Ajouter les amenities au lieu 1
                if pool:
                    place1.amenities.append(pool)
                if ac:
                    place1.amenities.append(ac)
                if tv:
                    place1.amenities.append(tv)
                if wifi:
                    place1.amenities.append(wifi)
                db.session.commit()
                
                # Lieu 2 : Beach House (avec WiFi, parking, cuisine)
                place2 = facade.create_place({
                    "title": "Beach House",
                    "description": "Cozy beach house steps from the ocean",
                    "price": 200.0,
                    "latitude": 43.6047,
                    "longitude": 1.4442,
                    "owner_id": existing_user.id
                })
                
                # Ajouter les amenities au lieu 2
                if wifi:
                    place2.amenities.append(wifi)
                if parking:
                    place2.amenities.append(parking)
                if kitchen:
                    place2.amenities.append(kitchen)
                db.session.commit()
                
                # Lieu 3 : Mountain Cabin (avec WiFi, parking, cuisine, AC)
                place3 = facade.create_place({
                    "title": "Mountain Cabin",
                    "description": "Rustic cabin in the mountains",
                    "price": 80.0,
                    "latitude": 45.7640,
                    "longitude": 4.8357,
                    "owner_id": existing_user.id
                })
                
                # Ajouter les amenities au lieu 3
                if wifi:
                    place3.amenities.append(wifi)
                if parking:
                    place3.amenities.append(parking)
                if kitchen:
                    place3.amenities.append(kitchen)
                if ac:
                    place3.amenities.append(ac)
                db.session.commit()
                
                print("Test places created with amenities")
            except Exception as e:
                print(f"Could not create test places: {e}")
                import traceback
                traceback.print_exc()
    
    return app