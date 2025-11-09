from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import request
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
        try:
            credentials = request.get_json()
            
            print("\n LOGIN ATTEMPT")
            print(f"Credentials: {credentials}")
            
            if not credentials:
                return {'error': 'No data provided'}, 400
            
            email = credentials.get('email')
            password = credentials.get('password')
            
            if not email or not password:
                return {'error': 'Email and password are required'}, 400
            
            print(f"Email: {email}")
            
            user = facade.get_user_by_email(email)
            
            if not user:
                print(f"User not found: {email}")
                return {'error': 'Invalid credentials'}, 401
            
            print(f"User found: {user.id}")
            
            if not user.verify_password(password):
                print("Invalid password")
                return {'error': 'Invalid credentials'}, 401
            
            print("Authentication successful")
            
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"is_admin": user.is_admin}
            )
            
            print(f"Token created")
            
            return {'access_token': access_token}, 200
            
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': 'Internal server error', 'details': str(e)}, 500

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
