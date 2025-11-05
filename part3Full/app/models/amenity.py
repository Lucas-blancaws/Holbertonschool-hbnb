from app.models.basemodel import BaseModel
from app.extensions import db
from sqlalchemy.orm import validates

class Amenity(BaseModel):
    """Amenity model for SQLAlchemy"""
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        """Initialize Amenity with name"""
        super().__init__()
        self.name = name

    @validates('name')
    def validate_name(self, key, value):
        """Validate name field"""
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        if not value:
            raise ValueError("Name cannot be empty")
        if len(value) > 50:
            raise ValueError("Name must be 50 characters max.")
        return value

    def to_dict(self):
        """Convert amenity to dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
