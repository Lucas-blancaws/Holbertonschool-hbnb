from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import current_app
from app.services.facade_instance import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(400, 'Invalid input')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        
        # Validation des champs requis
        if not credentials or not credentials.get('email') or not credentials.get('password'):
            return {'error': 'Email and password are required'}, 400
        
        email = credentials['email'].strip().lower()
        password = credentials['password']
        
        try:
            user = facade.get_user_by_email(email)
        except Exception as e:
            if current_app.config.get('DEBUG'):
                print(f"Error fetching user: {e}")
            return {'error': 'Internal server error'}, 500
        
        # Debug seulement en développement
        if current_app.config.get('DEBUG'):
            print(f"Login attempt for: {email}")
            print(f"User found: {user is not None}")
        
        if not user or not user.verify_password(password):
            return {'error': 'Invalid credentials'}, 401
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )
        
        return {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin
            }
        }, 200


@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    def get(self):
        """Example of a protected route"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        return {
            "message": f"Hello, user {current_user}",
            "is_admin": claims.get("is_admin", False)
        }, 200