from flask_restx import Namespace, Resource, fields
from app.services.facade_instance import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self):
        """Register a new review"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        review_data = api.payload

        # If not admin, user can only create reviews for themselves
        if not is_admin:
            if 'user_id' in review_data and review_data['user_id'] != current_user_id:
                return {'error': 'Unauthorized action'}, 403
            review_data['user_id'] = current_user_id

        place_id = review_data.get('place_id')
        if not place_id:
            return {'error': 'place_id is required'}, 400

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        user_id = review_data.get('user_id', current_user_id)
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 400

        # Admins can bypass these restrictions
        if not is_admin:
            # Regular users cannot review their own place
            if str(place.owner.id) == current_user_id:
                return {'error': 'You cannot review your own place'}, 400
            
            # Regular users can only review once per place
            try:
                existing_reviews = facade.get_reviews_by_place(place.id)
                for review in existing_reviews:
                    if str(review.user.id) == current_user_id:
                        return {'error': 'You have already reviewed this place'}, 400
            except Exception:
                pass

        try:
            new_review = facade.create_review(review_data)
            return new_review.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        return [review.to_dict() for review in facade.get_all_reviews()], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, review_id):
        """Update a review's information"""
        review_data = api.payload
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Admin can modify any review, regular users only their own
        if not is_admin and str(review.user.id) != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        # Nobody can change user_id or place_id
        if 'user_id' in review_data or 'place_id' in review_data:
            return {'error': 'You cannot change user_id or place_id'}, 400
        
        try:
            facade.update_review(review_id, api.payload)
            return {'message': 'Review updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Admin can delete any review, regular users only their own
        if not is_admin and str(review.user.id) != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.delete_review(review_id)
            return {'message': 'Review deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 400
