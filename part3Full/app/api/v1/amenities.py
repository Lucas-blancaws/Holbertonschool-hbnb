from flask_restx import Namespace, Resource, fields
from app.services.facade_instance import facade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Logic to create a new amenity
        pass

@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @jwt_required()
    def put(self, amenity_id):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        # Logic to update an amenity
        pass

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model)
    @api.response(201, 'Amenity successfully created')
    @api.response(403, 'Admin privileges required')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Create a new amenity (ADMIN ONLY)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        if not is_admin:
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload
        
        existing_amenity = facade.amenity_repo.get_by_attribute('name', amenity_data.get('name'))
        if existing_amenity:
            return {'error': 'Amenity already exists'}, 400
        
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return new_amenity.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of amenities retrieved successfully')
    def get(self):
        """Retrieve a list of all amenities (PUBLIC)"""
        amenities = facade.get_all_amenities()
        return [amenity.to_dict() for amenity in amenities], 200


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID (PUBLIC)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated successfully')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity (ADMIN ONLY)"""
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        
        if not is_admin:
            return {'error': 'Admin privileges required'}, 403

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404

        amenity_data = api.payload
        try:
            facade.update_amenity(amenity_id, amenity_data)
            updated_amenity = facade.get_amenity(amenity_id)
            return updated_amenity.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 400
