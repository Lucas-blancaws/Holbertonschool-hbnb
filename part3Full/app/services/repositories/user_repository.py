from app.models.user import User
from app.persistence.repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    """
    Repository for User entity
    Provides user-specific database operations
    """
    
    def __init__(self):
        """Initialize UserRepository with User model"""
        super().__init__(User)

    def get_user_by_email(self, email):
        """
        Retrieve a user by email address
        
        Args:
            email (str): The email address to search for
            
        Returns:
            User: The user object if found, None otherwise
        """
        return self.model.query.filter_by(email=email).first()

    def get_all_admins(self):
        """
        Retrieve all admin users
        
        Returns:
            list: List of admin users
        """
        return self.model.query.filter_by(is_admin=True).all()

    def email_exists(self, email):
        """
        Check if an email already exists in the database
        
        Args:
            email (str): The email to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        return self.model.query.filter_by(email=email).first() is not None
