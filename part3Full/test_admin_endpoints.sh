#!/bin/bash

BASE_URL="http://127.0.0.1:5000/api/v1"

echo "=========================================="
echo "Testing Admin Endpoints"
echo "=========================================="
echo ""

# 1. Login as Admin
echo "1. Login as Admin..."
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john2.doe@example.com",
    "password": "123456"
  }')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Failed to get admin token"
    echo "Response: $ADMIN_RESPONSE"
    exit 1
fi

echo "✅ Admin token obtained"
echo ""

# 2. Create a new user as admin
echo "2. Creating a new user as admin..."
NEW_USER_RESPONSE=$(curl -s -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "password": "password123"
  }')

echo "Response: $NEW_USER_RESPONSE"
NEW_USER_ID=$(echo $NEW_USER_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo ""

# 3. Try to create user without admin token (should fail)
echo "3. Trying to create user without being admin (should fail)..."

# First create a regular user to test
REGULAR_USER=$(curl -s -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "first_name": "Regular",
    "last_name": "User",
    "email": "regular@example.com",
    "password": "password123"
  }')

# Login as regular user
REGULAR_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "regular@example.com",
    "password": "password123"
  }')

REGULAR_TOKEN=$(echo $REGULAR_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

FAIL_RESPONSE=$(curl -s -X POST "$BASE_URL/users/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -d '{
    "first_name": "Should",
    "last_name": "Fail",
    "email": "shouldfail@example.com",
    "password": "password123"
  }')

echo "Response: $FAIL_RESPONSE"
echo ""

# 4. Update user email as admin
echo "4. Updating user email as admin..."
if [ ! -z "$NEW_USER_ID" ]; then
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/users/$NEW_USER_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{
      "email": "jane.updated@example.com",
      "first_name": "Jane Updated"
    }')
  echo "Response: $UPDATE_RESPONSE"
fi
echo ""

# 5. Create amenity as admin
echo "5. Creating amenity as admin..."
AMENITY_RESPONSE=$(curl -s -X POST "$BASE_URL/amenities/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "name": "Swimming Pool"
  }')

echo "Response: $AMENITY_RESPONSE"
AMENITY_ID=$(echo $AMENITY_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo ""

# 6. Try to create amenity as regular user (should fail)
echo "6. Trying to create amenity as regular user (should fail)..."
FAIL_AMENITY=$(curl -s -X POST "$BASE_URL/amenities/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -d '{
    "name": "Gym"
  }')

echo "Response: $FAIL_AMENITY"
echo ""

# 7. Update amenity as admin
echo "7. Updating amenity as admin..."
if [ ! -z "$AMENITY_ID" ]; then
  UPDATE_AMENITY=$(curl -s -X PUT "$BASE_URL/amenities/$AMENITY_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{
      "name": "Olympic Swimming Pool"
    }')
  echo "Response: $UPDATE_AMENITY"
fi
echo ""

# 8. Create a place as regular user
echo "8. Creating a place as regular user..."
PLACE_RESPONSE=$(curl -s -X POST "$BASE_URL/places/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REGULAR_TOKEN" \
  -d '{
    "title": "Cozy Apartment",
    "description": "A nice place to stay",
    "price": 100.0,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "amenities": []
  }')

echo "Response: $PLACE_RESPONSE"
PLACE_ID=$(echo $PLACE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo ""

# 9. Admin modifies place owned by regular user
echo "9. Admin modifying place owned by regular user..."
if [ ! -z "$PLACE_ID" ]; then
  ADMIN_UPDATE_PLACE=$(curl -s -X PUT "$BASE_URL/places/$PLACE_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{
      "title": "Admin Updated Title",
      "price": 150.0
    }')
  echo "Response: $ADMIN_UPDATE_PLACE"
fi
echo ""

# 10. Create review as regular user
echo "10. Creating review as regular user on their own place (should fail)..."
if [ ! -z "$PLACE_ID" ]; then
  REVIEW_FAIL=$(curl -s -X POST "$BASE_URL/reviews/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $REGULAR_TOKEN" \
    -d '{
      "text": "Great place!",
      "rating": 5,
      "place_id": "'$PLACE_ID'"
    }')
  echo "Response: $REVIEW_FAIL"
fi
echo ""

# 11. Admin creates review on any place (bypassing ownership restriction)
echo "11. Admin creating review on place (bypassing restriction)..."
if [ ! -z "$PLACE_ID" ]; then
  ADMIN_REVIEW=$(curl -s -X POST "$BASE_URL/reviews/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d '{
      "text": "Admin can review anything!",
      "rating": 5,
      "place_id": "'$PLACE_ID'"
    }')
  echo "Response: $ADMIN_REVIEW"
  REVIEW_ID=$(echo $ADMIN_REVIEW | grep -o '"id":"[^"]*' | cut -d'"' -f4)
fi
echo ""

# 12. Admin deletes any review
echo "12. Admin deleting any review..."
if [ ! -z "$REVIEW_ID" ]; then
  DELETE_REVIEW=$(curl -s -X DELETE "$BASE_URL/reviews/$REVIEW_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  echo "Response: $DELETE_REVIEW"
fi
echo ""

echo "=========================================="
echo "Admin endpoint testing complete!"
echo "=========================================="
