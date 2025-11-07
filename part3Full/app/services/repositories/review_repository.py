from app.models.review import Review
from app.persistence.repository import SQLAlchemyRepository

class ReviewRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Review)
    
    def get_by_place(self, place_id):
        """Get all reviews for a specific place"""
        return self.model.query.filter_by(place_id=place_id).all()
