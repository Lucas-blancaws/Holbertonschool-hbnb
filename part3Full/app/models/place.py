from app.models.basemodel import BaseModel
from sqlalchemy.orm import validates, relationship
from app.extensions import db
from app.models.place_amenity import place_amenity

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    reviews = relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    amenities = relationship('Amenity', secondary=place_amenity, lazy='subquery',
                             backref=db.backref('places', lazy=True))
    
    def __init__(self, title, price, latitude, longitude, owner, description=None):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner  
        self.owner_id = owner.id if hasattr(owner, 'id') else owner
        self.reviews = []
        self.amenities = []
    
    @validates('title')
    def validate_title(self, key, value):
        """Valide le titre du place"""
        if not value:
            raise ValueError("Title cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        if len(value) > 100:
            raise ValueError("Title must be 100 characters max.")
        return value
    
    @validates('price')
    def validate_price(self, key, value):
        """Valide le prix"""
        if not isinstance(value, (float, int)):
            raise TypeError("Price must be a float or int")
        if value <= 0:
            raise ValueError("Price must be positive.")
        return float(value)
    
    @validates('latitude')
    def validate_latitude(self, key, value):
        """Valide la latitude"""
        if not isinstance(value, (float, int)):
            raise TypeError("Latitude must be a float")
        value = float(value)
        if not -90.0 <= value <= 90.0:
            raise ValueError("Latitude must be between -90 and 90")
        return value
    
    @validates('longitude')
    def validate_longitude(self, key, value):
        """Valide la longitude"""
        if not isinstance(value, (float, int)):
            raise TypeError("Longitude must be a float")
        value = float(value)
        if not -180.0 <= value <= 180.0:
            raise ValueError("Longitude must be between -180 and 180")
        return value

    def add_review(self, review):
        """Ajoute une review au place"""
        self.reviews.append(review)
    
    def delete_review(self, review):
        """Supprime une review du place"""
        self.reviews.remove(review)

    def add_amenity(self, amenity):
        """Ajoute une amenity au place"""
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': str(self.owner_id)
        }
    
    def to_dict_list(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict() if hasattr(self, 'owner') and self.owner else {'id': self.owner_id},
            'amenities': [a.to_dict() if hasattr(a, 'to_dict') else a for a in self.amenities],
            'reviews': [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.reviews]
        }
