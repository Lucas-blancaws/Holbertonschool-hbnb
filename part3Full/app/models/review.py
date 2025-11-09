from app.models.basemodel import BaseModel
from sqlalchemy.orm import validates
from app.extensions import db

class Review(BaseModel):
    __tablename__ = 'reviews'
    
    text = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.place_id = place.id
        self.user = user
        self.user_id = user.id
    
    @validates('text')
    def validate_text(self, key, value):
        if not value:
            raise ValueError("Text cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Text must be a string")
        if len(value) > 500:
            raise ValueError("Text must be 500 characters max.")
        return value
    
    @validates('rating')
    def validate_rating(self, key, value):
        if not isinstance(value, int):
            raise TypeError("Rating must be an integer")
        if not 1 <= value <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return value

    def to_dict(self):
        return {
            'id': str(self.id),
            'text': self.text,
            'rating': self.rating,
            'place_id': str(self.place_id),
            'user_id': str(self.user_id)
        }
