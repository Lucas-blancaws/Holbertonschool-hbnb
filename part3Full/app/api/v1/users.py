from flask_restx import Namespace, Resource, fields
from app.services.facade_instance import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(description='Password of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'Email already registered')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Create a new user (ADMIN ONLY)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        if not is_admin:
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload

        if 'password' not in user_data:
            return {'error': 'Password is required'}, 400

        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 409

        try:
            new_user = facade.create_user(user_data)
            return new_user.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400
        
    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of users (PUBLIC)"""
        users = facade.get_users()
        return [user.to_dict() for user in users], 200
    
@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID (PUBLIC)"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @jwt_required()
    def put(self, user_id):
        """Update a user's information"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Admin can modify anyone, regular user only themselves
        if not is_admin and current_user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        user_data = api.payload

        # Regular users cannot modify email and password
        if not is_admin:
            if 'email' in user_data:
                return {'error': 'You cannot modify email'}, 400
            if 'password' in user_data:
                return {'error': 'You cannot modify password'}, 400

        # Admin can modify email, but must check uniqueness
        if is_admin and 'email' in user_data:
            existing_user = facade.get_user_by_email(user_data['email'])
            if existing_user and str(existing_user.id) != user_id:
                return {'error': 'Email already in use'}, 400

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        # Admin can modify password - hash it
        if is_admin and 'password' in user_data:
            user.hash_password(user_data['password'])
            del user_data['password']

        try:
            facade.update_user(user_id, user_data)
            updated_user = facade.get_user(user_id)
            return updated_user.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 400
