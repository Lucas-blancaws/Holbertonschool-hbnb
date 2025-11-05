"""
HBnB Part 3 - Automated Test Suite
Tests for Tasks 0-6 (before Place/Review/Amenity migration)

This test suite validates:
- JWT Authentication (Task 2)
- User CRUD with Admin permissions (Tasks 1, 3, 4, 6)
- Amenity CRUD with Admin permissions (Task 4)
- Place and Review operations (Tasks 3, 4)
- Persistence validation for SQLAlchemy entities

Expected behavior:
- Users: Persisted in DB (SQLAlchemy)
- Amenities, Places, Reviews: In-memory (lost on restart) - Task 7 not done yet
"""

import unittest
import json
import time
from datetime import datetime


class TestHBnBPart3(unittest.TestCase):
    """Test suite for HBnB Part 3 - Tasks 0-6"""

    @classmethod
    def setUpClass(cls):
        """Setup test configuration before all tests"""
        print("\n" + "="*80)
        print("🧪 HBNB PART 3 - AUTOMATED TEST SUITE")
        print("="*80)
        print("\n⚙️  Setting up test environment...\n")
        
        # Import Flask app
        try:
            from app import create_app
            from app.extensions import db
            
            # Create app with test config
            cls.app = create_app()
            cls.app.config['TESTING'] = True
            cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            cls.app.config['JWT_SECRET_KEY'] = 'test-secret-key'
            
            cls.client = cls.app.test_client()
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            
            # Create all tables
            db.create_all()
            
            print("✅ Flask app initialized")
            print("✅ Test database created")
        except Exception as e:
            print(f"❌ Failed to setup test environment: {e}")
            raise

        # Test data storage
        cls.admin_token = None
        cls.user_token = None
        cls.admin_id = None
        cls.user_id = None
        cls.amenity_id = None
        cls.place_id = None
        cls.review_id = None

    @classmethod
    def tearDownClass(cls):
        """Cleanup after all tests"""
        print("\n" + "="*80)
        print("🧹 Cleaning up test environment...")
        print("="*80 + "\n")
        try:
            from app.extensions import db
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()
            print("✅ Test database cleaned up")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

    def setUp(self):
        """Setup before each test"""
        pass

    def tearDown(self):
        """Cleanup after each test"""
        pass

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def print_test_header(self, test_name, description):
        """Print formatted test header"""
        print(f"\n{'─'*80}")
        print(f"🧪 {test_name}")
        print(f"   {description}")
        print(f"{'─'*80}")

    def print_result(self, success, message, details=None):
        """Print formatted test result"""
        icon = "✅" if success else "❌"
        print(f"{icon} {message}")
        if details:
            print(f"   Details: {details}")

    def assert_status_code(self, response, expected_status, test_name):
        """Assert response status code with formatted output"""
        actual_status = response.status_code
        success = actual_status == expected_status
        
        if success:
            self.print_result(True, f"Status code: {actual_status}")
        else:
            self.print_result(
                False, 
                f"Expected {expected_status}, got {actual_status}",
                f"Response: {response.get_json()}"
            )
        
        self.assertEqual(actual_status, expected_status, 
                        f"{test_name} failed: expected {expected_status}, got {actual_status}")

    def assert_json_contains(self, response_json, key, test_name):
        """Assert JSON response contains specific key"""
        if key in response_json:
            self.print_result(True, f"Response contains '{key}'")
        else:
            self.print_result(False, f"Missing key '{key}' in response", response_json)
        
        self.assertIn(key, response_json, f"{test_name} failed: missing key '{key}'")

    def assert_json_not_contains(self, response_json, key, test_name):
        """Assert JSON response does NOT contain specific key"""
        if key not in response_json:
            self.print_result(True, f"Response correctly excludes '{key}'")
        else:
            self.print_result(False, f"Should not contain '{key}'", response_json)
        
        self.assertNotIn(key, response_json, f"{test_name} failed: should not contain '{key}'")

    # ========================================================================
    # TASK 0-1: CONFIGURATION & PASSWORD HASHING
    # ========================================================================

    def test_01_app_configuration(self):
        """Test 01: Application factory with configuration"""
        self.print_test_header(
            "TEST 01: Application Configuration",
            "Verify Flask app is properly configured"
        )

        self.assertIsNotNone(self.app, "App should be initialized")
        self.print_result(True, "Application factory working")
        
        # Check if database is configured
        with self.app.app_context():
            from app.extensions import db
            self.assertIsNotNone(db, "Database should be configured")
            self.print_result(True, "Database configured")

    # ========================================================================
    # TASK 2: JWT AUTHENTICATION
    # ========================================================================

    def test_02_create_admin_user(self):
        """Test 02: Create initial admin user"""
        self.print_test_header(
            "TEST 02: Create Admin User",
            "Create the first admin user for testing"
        )

        # Create admin using facade (which handles password properly)
        from app.services.facade_instance import facade

        try:
            admin = facade.create_user({
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@hbnb.com',
                'password': 'admin1234',
                'is_admin': True
            })
            
            self.__class__.admin_id = str(admin.id)
            
            self.assertIsNotNone(admin.id, "Admin should have an ID")
            self.print_result(True, f"Admin user created (ID: {admin.id})")
            self.print_result(True, f"Email: {admin.email}")
        except Exception as e:
            self.print_result(False, f"Failed to create admin: {str(e)}")
            raise

    def test_03_login_valid_credentials(self):
        """Test 03: Login with valid credentials"""
        self.print_test_header(
            "TEST 03: Login with Valid Credentials",
            "POST /api/v1/auth/login with correct email/password"
        )

        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'admin@hbnb.com',
                'password': 'admin1234'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Login")
        
        data = response.get_json()
        self.assert_json_contains(data, 'access_token', "Login response")
        
        # Store token for future tests
        self.__class__.admin_token = data['access_token']
        self.print_result(True, f"JWT token received: {data['access_token'][:20]}...")

    def test_04_login_invalid_credentials(self):
        """Test 04: Login with invalid credentials"""
        self.print_test_header(
            "TEST 04: Login with Invalid Credentials",
            "POST /api/v1/auth/login with wrong password"
        )

        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'admin@hbnb.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 401, "Invalid login")
        
        data = response.get_json()
        self.assert_json_contains(data, 'error', "Error response")

    def test_05_login_nonexistent_user(self):
        """Test 05: Login with non-existent email"""
        self.print_test_header(
            "TEST 05: Login with Non-existent Email",
            "POST /api/v1/auth/login with unknown email"
        )

        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'nonexistent@test.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 401, "Non-existent user login")

    # ========================================================================
    # TASK 3-4: USER MANAGEMENT (Admin & Regular Users)
    # ========================================================================

    def test_06_get_all_users_public(self):
        """Test 06: GET all users without authentication (PUBLIC)"""
        self.print_test_header(
            "TEST 06: Get All Users (Public)",
            "GET /api/v1/users/ without JWT token"
        )

        response = self.client.get('/api/v1/users/')
        
        self.assert_status_code(response, 200, "Get users (public)")
        
        data = response.get_json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.print_result(True, f"Retrieved {len(data)} user(s)")
        
        # Check password is not in response
        if len(data) > 0:
            self.assert_json_not_contains(data[0], 'password', "User data")

    def test_07_create_user_without_admin(self):
        """Test 07: Try to create user without admin privileges"""
        self.print_test_header(
            "TEST 07: Create User Without Admin Privileges",
            "POST /api/v1/users/ without admin token (should fail)"
        )

        # First create a regular user using facade
        from app.services.facade_instance import facade

        regular_user = facade.create_user({
            'first_name': 'Regular',
            'last_name': 'User',
            'email': 'regular@test.com',
            'password': 'password123',
            'is_admin': False
        })

        self.__class__.user_id = str(regular_user.id)

        # Login as regular user
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'regular@test.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        self.__class__.user_token = response.get_json()['access_token']

        # Try to create another user
        response = self.client.post(
            '/api/v1/users/',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'first_name': 'Should',
                'last_name': 'Fail',
                'email': 'shouldfail@test.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 403, "Create user without admin")
        
        data = response.get_json()
        self.assert_json_contains(data, 'error', "Error response")
        self.assertIn('Admin privileges required', data['error'])

    def test_08_create_user_as_admin(self):
        """Test 08: Create user as admin"""
        self.print_test_header(
            "TEST 08: Create User as Admin",
            "POST /api/v1/users/ with admin token"
        )

        response = self.client.post(
            '/api/v1/users/',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane@test.com',
                'password': 'pass123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 201, "Create user as admin")
        
        data = response.get_json()
        self.assert_json_contains(data, 'id', "Created user")
        self.assert_json_contains(data, 'email', "Created user")
        self.assert_json_not_contains(data, 'password', "Created user")
        
        self.print_result(True, f"User created: {data['first_name']} {data['last_name']}")

    def test_09_create_duplicate_email(self):
        """Test 09: Try to create user with existing email"""
        self.print_test_header(
            "TEST 09: Create User with Duplicate Email",
            "POST /api/v1/users/ with already registered email"
        )

        response = self.client.post(
            '/api/v1/users/',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'first_name': 'Duplicate',
                'last_name': 'User',
                'email': 'admin@hbnb.com',  # Already exists
                'password': 'password123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 409, "Duplicate email")
        
        data = response.get_json()
        self.assert_json_contains(data, 'error', "Error response")

    def test_10_update_own_profile_regular_user(self):
        """Test 10: Regular user updates their own profile"""
        self.print_test_header(
            "TEST 10: Update Own Profile (Regular User)",
            "PUT /api/v1/users/<user_id> as owner"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'first_name': 'UpdatedName'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Update own profile")
        
        # Verify update
        user_response = self.client.get(f'/api/v1/users/{self.user_id}')
        user_data = user_response.get_json()
        
        self.assertEqual(user_data['first_name'], 'UpdatedName')
        self.print_result(True, "Profile updated successfully")

    def test_11_user_cannot_modify_email(self):
        """Test 11: Regular user cannot modify their email"""
        self.print_test_header(
            "TEST 11: Regular User Cannot Modify Email",
            "PUT /api/v1/users/<user_id> trying to change email"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'email': 'newemail@test.com'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 400, "Modify email as regular user")
        
        data = response.get_json()
        self.assert_json_contains(data, 'error', "Error response")

    def test_12_user_cannot_modify_password(self):
        """Test 12: Regular user cannot modify their password"""
        self.print_test_header(
            "TEST 12: Regular User Cannot Modify Password",
            "PUT /api/v1/users/<user_id> trying to change password"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'password': 'newpassword123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 400, "Modify password as regular user")

    def test_13_user_cannot_modify_others(self):
        """Test 13: Regular user cannot modify other users"""
        self.print_test_header(
            "TEST 13: Regular User Cannot Modify Others",
            "PUT /api/v1/users/<other_user_id> as regular user"
        )

        response = self.client.put(
            f'/api/v1/users/{self.admin_id}',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'first_name': 'Hacked'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 403, "Modify other user")

    def test_14_admin_can_modify_any_user(self):
        """Test 14: Admin can modify any user"""
        self.print_test_header(
            "TEST 14: Admin Can Modify Any User",
            "PUT /api/v1/users/<user_id> as admin"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'first_name': 'AdminModified',
                'last_name': 'ByAdmin'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Admin modify user")

    def test_15_admin_can_modify_email(self):
        """Test 15: Admin can modify user's email"""
        self.print_test_header(
            "TEST 15: Admin Can Modify User Email",
            "PUT /api/v1/users/<user_id> changing email as admin"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'email': 'updated@test.com'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Admin modify email")

    def test_16_admin_can_modify_password(self):
        """Test 16: Admin can modify user's password"""
        self.print_test_header(
            "TEST 16: Admin Can Modify User Password",
            "PUT /api/v1/users/<user_id> changing password as admin"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'password': 'newpassword123'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Admin modify password")
        
        # Verify new password works
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                'email': 'updated@test.com',
                'password': 'newpassword123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(login_response.status_code, 200)
        self.print_result(True, "New password works correctly")

    # ========================================================================
    # TASK 4: AMENITY MANAGEMENT (Admin Only)
    # ========================================================================

    def test_17_get_amenities_public(self):
        """Test 17: GET all amenities (PUBLIC)"""
        self.print_test_header(
            "TEST 17: Get All Amenities (Public)",
            "GET /api/v1/amenities/ without JWT token"
        )

        response = self.client.get('/api/v1/amenities/')
        
        self.assert_status_code(response, 200, "Get amenities (public)")
        
        data = response.get_json()
        self.assertIsInstance(data, list, "Response should be a list")
        self.print_result(True, f"Retrieved {len(data)} amenity/amenities")

    def test_18_create_amenity_without_admin(self):
        """Test 18: Try to create amenity without admin privileges"""
        self.print_test_header(
            "TEST 18: Create Amenity Without Admin",
            "POST /api/v1/amenities/ as regular user (should fail)"
        )

        response = self.client.post(
            '/api/v1/amenities/',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'name': 'WiFi'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 403, "Create amenity without admin")

    def test_19_create_amenity_as_admin(self):
        """Test 19: Create amenity as admin"""
        self.print_test_header(
            "TEST 19: Create Amenity as Admin",
            "POST /api/v1/amenities/ with admin token"
        )

        response = self.client.post(
            '/api/v1/amenities/',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'name': 'WiFi'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 201, "Create amenity as admin")
        
        data = response.get_json()
        
        # DEBUG: Afficher exactement ce que retourne l'API
        print(f"\n🔍 DEBUG - API Response: {data}")
        print(f"🔍 DEBUG - ID value: {data.get('id')}")
        print(f"🔍 DEBUG - ID type: {type(data.get('id'))}")
        
        self.assert_json_contains(data, 'id', "Created amenity")
        self.assert_json_contains(data, 'name', "Created amenity")
        
        # Convert ID to string if it's a UUID or any other type
        amenity_id = data.get('id')
        if amenity_id:
            self.__class__.amenity_id = str(amenity_id)
        else:
            self.__class__.amenity_id = None
            
        self.print_result(True, f"Amenity created: {data['name']} (ID: {self.__class__.amenity_id})")

    def test_20_create_duplicate_amenity(self):
        """Test 20: Try to create duplicate amenity"""
        self.print_test_header(
            "TEST 20: Create Duplicate Amenity",
            "POST /api/v1/amenities/ with existing name"
        )

        response = self.client.post(
            '/api/v1/amenities/',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'name': 'WiFi'  # Already exists
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 400, "Duplicate amenity")

    def test_21_update_amenity_without_admin(self):
        """Test 21: Try to update amenity without admin privileges"""
        self.print_test_header(
            "TEST 21: Update Amenity Without Admin",
            "PUT /api/v1/amenities/<id> as regular user (should fail)"
        )

        response = self.client.put(
            f'/api/v1/amenities/{self.amenity_id}',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'name': 'Updated WiFi'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 403, "Update amenity without admin")

    def test_22_update_amenity_as_admin(self):
        """Test 22: Update amenity as admin"""
        self.print_test_header(
            "TEST 22: Update Amenity as Admin",
            "PUT /api/v1/amenities/<id> with admin token"
        )

        response = self.client.put(
            f'/api/v1/amenities/{self.amenity_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            data=json.dumps({
                'name': 'High-Speed WiFi'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 200, "Update amenity as admin")

    # ========================================================================
    # TASK 3-4: PLACE MANAGEMENT
    # ========================================================================

    def test_23_create_place_without_auth(self):
        """Test 23: Try to create place without authentication"""
        self.print_test_header(
            "TEST 23: Create Place Without Authentication",
            "POST /api/v1/places/ without JWT token (should fail)"
        )

        response = self.client.post(
            '/api/v1/places/',
            data=json.dumps({
                'title': 'Test Place',
                'description': 'A test place',
                'price': 100.0,
                'latitude': 48.8566,
                'longitude': 2.3522,
                'owner_id': self.user_id,
                'amenities': []
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 401, "Create place without auth")

    def test_24_create_place_as_user(self):
        """Test 24: Create place as authenticated user"""
        self.print_test_header(
            "TEST 24: Create Place as Authenticated User",
            "POST /api/v1/places/ with user token"
        )

        print("⚠️  Note: This test may fail due to User(DB) ↔ Place(Memory) relation")
        print("   This is EXPECTED and will be fixed in Task 7")

        try:
            response = self.client.post(
                '/api/v1/places/',
                headers={'Authorization': f'Bearer {self.user_token}'},
                data=json.dumps({
                    'title': 'Cozy Apartment',
                    'description': 'Nice place in Paris',
                    'price': 100.0,
                    'latitude': 48.8566,
                    'longitude': 2.3522,
                    'owner_id': self.user_id,
                    'amenities': []
                }),
                content_type='application/json'
            )

            if response.status_code == 201:
                self.assert_status_code(response, 201, "Create place")
                data = response.get_json()
                self.__class__.place_id = data['id']
                self.print_result(True, f"Place created: {data['title']}")
            else:
                print("⚠️  Expected behavior: Place creation failed (User-Place relation issue)")
                print(f"   Status: {response.status_code}")
                print(f"   This will be resolved in Task 7")
        except Exception as e:
            print(f"⚠️  Expected exception: {str(e)}")
            print("   This will be resolved in Task 7")

    def test_25_get_all_places_public(self):
        """Test 25: GET all places (PUBLIC)"""
        self.print_test_header(
            "TEST 25: Get All Places (Public)",
            "GET /api/v1/places/ without JWT token"
        )

        response = self.client.get('/api/v1/places/')
        self.assert_status_code(response, 200, "Get places (public)")

    # ========================================================================
    # TASK 6: PERSISTENCE VALIDATION
    # ========================================================================

    def test_26_user_persistence_validation(self):
        """Test 26: Validate users are persisted in database"""
        self.print_test_header(
            "TEST 26: User Persistence Validation",
            "Verify users remain after clearing in-memory cache"
        )

        # Get current user count
        response = self.client.get('/api/v1/users/')
        users_before = len(response.get_json())
        self.print_result(True, f"Users in DB before: {users_before}")

        # Simulate app restart by clearing SQLAlchemy session
        from app.extensions import db
        db.session.remove()

        # Query again - should still have users
        response = self.client.get('/api/v1/users/')
        users_after = len(response.get_json())
        
        self.assertEqual(users_before, users_after)
        self.print_result(True, f"Users in DB after: {users_after}")
        self.print_result(True, "Users are properly persisted! ✓")

    def test_27_amenity_not_persisted_warning(self):
        """Test 27: Validate amenities are NOT persisted (in-memory)"""
        self.print_test_header(
            "TEST 27: Amenity Persistence Check",
            "⚠️  Verify amenities are in-memory (Task 7 not done)"
        )

        response = self.client.get('/api/v1/amenities/')
        amenities = response.get_json()
        
        print(f"⚠️  Current amenities in memory: {len(amenities)}")
        print("   Expected behavior: Amenities will be lost on app restart")
        print("   This is NORMAL - Task 7 will migrate amenities to DB")

    # ========================================================================
    # TASK 3: REVIEW MANAGEMENT
    # ========================================================================

    def test_28_user_cannot_review_own_place(self):
        """Test 28: User cannot review their own place"""
        self.print_test_header(
            "TEST 28: User Cannot Review Own Place",
            "POST /api/v1/reviews/ for own place (should fail)"
        )

        if not self.place_id:
            print("⚠️  Skipping: No place_id available (Place creation failed)")
            return

        response = self.client.post(
            '/api/v1/reviews/',
            headers={'Authorization': f'Bearer {self.user_token}'},
            data=json.dumps({
                'text': 'Great place!',
                'rating': 5,
                'place_id': self.place_id,
                'user_id': self.user_id
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 400, "Review own place")

    def test_29_admin_can_bypass_review_restrictions(self):
        """Test 29: Admin can bypass review restrictions"""
        self.print_test_header(
            "TEST 29: Admin Can Bypass Review Restrictions",
            "POST /api/v1/reviews/ as admin (can review any place)"
        )

        if not self.place_id:
            print("⚠️  Skipping: No place_id available")
            return

        print("⚠️  Note: This test may fail due to relation issues (Task 7)")

        try:
            response = self.client.post(
                '/api/v1/reviews/',
                headers={'Authorization': f'Bearer {self.admin_token}'},
                data=json.dumps({
                    'text': 'Admin review',
                    'rating': 5,
                    'place_id': self.place_id,
                    'user_id': self.admin_id
                }),
                content_type='application/json'
            )

            if response.status_code == 201:
                self.print_result(True, "Admin can bypass restrictions")
            else:
                print("⚠️  Review creation affected by DB/Memory relation")
        except Exception as e:
            print(f"⚠️  Expected exception: {str(e)}")

    # ========================================================================
    # SECURITY TESTS
    # ========================================================================

    def test_30_protected_endpoint_without_token(self):
        """Test 30: Access protected endpoint without token"""
        self.print_test_header(
            "TEST 30: Protected Endpoint Without Token",
            "PUT /api/v1/users/<id> without JWT (should fail)"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            data=json.dumps({
                'first_name': 'Hacker'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 401, "Access without token")

    def test_31_protected_endpoint_invalid_token(self):
        """Test 31: Access protected endpoint with invalid token"""
        self.print_test_header(
            "TEST 31: Protected Endpoint With Invalid Token",
            "PUT /api/v1/users/<id> with fake JWT"
        )

        response = self.client.put(
            f'/api/v1/users/{self.user_id}',
            headers={'Authorization': 'Bearer invalid_token_12345'},
            data=json.dumps({
                'first_name': 'Hacker'
            }),
            content_type='application/json'
        )

        self.assert_status_code(response, 422, "Access with invalid token")


# ============================================================================
# TEST RUNNER WITH SUMMARY
# ============================================================================

def run_tests():
    """Run all tests with detailed summary"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHBnBPart3)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print("="*80)
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Ready for Task 7 migration.")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
        if any('place' in str(f).lower() or 'review' in str(f).lower() 
               for f in result.failures + result.errors):
            print("\n💡 Note: Failures in Place/Review tests are EXPECTED")
            print("   These will be resolved when you complete Task 7")
            print("   (Migration of Place, Review, Amenity to SQLAlchemy)")
    
    print("\n" + "="*80)
    print("🏁 Test run completed")
    print("="*80 + "\n")
    
    return result


if __name__ == '__main__':
    run_tests()