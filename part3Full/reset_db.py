#!/usr/bin/env python3
"""
Script de test COMPLET pour HBnB Part 3
Teste : Authentication, Authorization, CRUD, Validations
"""

import requests
import json
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Stats
tests_passed = 0
tests_failed = 0
tests_total = 0

# Storage
admin_token = None
user_token = None
created_ids = {
    'admin': None,
    'user': None,
    'place': None,
    'review': None,
    'amenity': None
}


def print_header(title):
    print(f"\n{'='*70}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(70)}")
    print(f"{'='*70}\n")


def print_test(test_name):
    global tests_total
    tests_total += 1
    print(f"{Fore.YELLOW}[TEST {tests_total}] {test_name}...", end=" ")


def print_success(message=""):
    global tests_passed
    tests_passed += 1
    print(f"{Fore.GREEN}✓ PASSED{Style.RESET_ALL} {message}")


def print_failure(message=""):
    global tests_failed
    tests_failed += 1
    print(f"{Fore.RED}✗ FAILED{Style.RESET_ALL} {message}")


def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


# ========== AUTHENTICATION TESTS ==========

def test_login_admin():
    """Test: Login avec admin"""
    print_test("Login admin")
    
    login_data = {
        "email": "john2.doe@example.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            global admin_token
            admin_token = data.get('access_token')
            
            if admin_token:
                created_ids['admin'] = data['user']['id']
                print_success(f"Admin token obtenu")
                return True
            else:
                print_failure("Token manquant dans la réponse")
                return False
        else:
            print_failure(f"Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_create_regular_user():
    """Test: Créer un user régulier (admin)"""
    print_test("Création user régulier par admin")
    
    if not admin_token:
        print_failure("Pas de token admin")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {admin_token}'
    
    user_data = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": f"alice.test{tests_total}@example.com",
        "password": "password123",
        "is_admin": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers_auth)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['user'] = data['id']
            print_success(f"User créé: {data['id'][:8]}...")
            return True
        else:
            print_failure(f"Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_login_regular_user():
    """Test: Login user régulier"""
    print_test("Login user régulier")
    
    login_data = {
        "email": f"alice.test{tests_total-1}@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            global user_token
            user_token = data.get('access_token')
            
            if user_token:
                print_success("User token obtenu")
                return True
            else:
                print_failure("Token manquant")
                return False
        else:
            print_failure(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


# ========== AMENITY TESTS ==========

def test_create_amenity_as_admin():
    """Test: Créer amenity (admin)"""
    print_test("Création amenity par admin")
    
    if not admin_token:
        print_failure("Pas de token admin")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {admin_token}'
    
    amenity_data = {"name": f"WiFi-Test-{tests_total}"}
    
    try:
        response = requests.post(f"{BASE_URL}/amenities/", json=amenity_data, headers=headers_auth)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['amenity'] = data['id']
            print_success(f"Amenity créée: {data['name']}")
            return True
        else:
            print_failure(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_create_amenity_as_user_forbidden():
    """Test: User régulier ne peut pas créer amenity"""
    print_test("User ne peut PAS créer amenity")
    
    if not user_token:
        print_failure("Pas de user token")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {user_token}'
    
    amenity_data = {"name": "Unauthorized-Amenity"}
    
    try:
        response = requests.post(f"{BASE_URL}/amenities/", json=amenity_data, headers=headers_auth)
        
        if response.status_code == 403:
            print_success("Accès refusé comme attendu")
            return True
        else:
            print_failure(f"Devrait être 403, mais: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


# ========== PLACE TESTS ==========

def test_create_place_as_user():
    """Test: User crée son propre place"""
    print_test("Création place par user")
    
    if not user_token or not created_ids['user']:
        print_failure("User token ou ID manquant")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {user_token}'
    
    place_data = {
        "title": "Cozy Apartment",
        "description": "Nice place",
        "price": 100.0,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": created_ids['user'],
        "amenities": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=headers_auth)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['place'] = data['id']
            print_success(f"Place créé: {data['title']}")
            return True
        else:
            print_failure(f"Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_user_cannot_create_place_for_others():
    """Test: User ne peut pas créer place pour quelqu'un d'autre"""
    print_test("User ne peut créer place pour autrui")
    
    if not user_token:
        print_failure("Pas de user token")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {user_token}'
    
    place_data = {
        "title": "Fake Place",
        "price": 50.0,
        "latitude": 40.0,
        "longitude": -3.0,
        "owner_id": created_ids['admin'],  # Essayer de créer pour admin
        "amenities": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=headers_auth)
        
        if response.status_code == 403:
            print_success("Accès refusé comme attendu")
            return True
        else:
            print_failure(f"Devrait être 403, mais: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_admin_can_create_place_for_others():
    """Test: Admin peut créer place pour n'importe qui"""
    print_test("Admin peut créer place pour autrui")
    
    if not admin_token or not created_ids['user']:
        print_failure("Token ou user ID manquant")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {admin_token}'
    
    place_data = {
        "title": "Admin Created Place",
        "price": 200.0,
        "latitude": 51.5074,
        "longitude": -0.1278,
        "owner_id": created_ids['user'],  # Créer pour le user
        "amenities": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=headers_auth)
        
        if response.status_code == 201:
            print_success("Admin peut créer place pour autrui")
            return True
        else:
            print_failure(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


# ========== REVIEW TESTS ==========

def test_create_review_as_admin():
    """Test: Admin crée une review"""
    print_test("Création review par admin")
    
    if not admin_token or not created_ids['place'] or not created_ids['admin']:
        print_failure("Données manquantes")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {admin_token}'
    
    review_data = {
        "text": "Great place!",
        "rating": 5,
        "place_id": created_ids['place'],
        "user_id": created_ids['admin']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers_auth)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['review'] = data['id']
            print_success(f"Review créée")
            return True
        else:
            print_failure(f"Status: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_user_cannot_review_own_place():
    """Test: User ne peut pas reviewer son propre place"""
    print_test("User ne peut reviewer son propre place")
    
    if not user_token or not created_ids['place'] or not created_ids['user']:
        print_failure("Données manquantes")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {user_token}'
    
    review_data = {
        "text": "My own place review",
        "rating": 5,
        "place_id": created_ids['place'],
        "user_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers_auth)
        
        if response.status_code == 400:
            print_success("Refusé comme attendu")
            return True
        else:
            print_failure(f"Devrait être 400, mais: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


# ========== VALIDATION TESTS ==========

def test_validation_negative_price():
    """Test: Prix négatif rejeté"""
    print_test("Validation: Prix négatif")
    
    if not user_token:
        print_failure("Pas de token")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {user_token}'
    
    place_data = {
        "title": "Invalid Place",
        "price": -50.0,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": created_ids['user'],
        "amenities": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=headers_auth)
        
        if response.status_code == 400:
            print_success("Prix négatif rejeté")
            return True
        else:
            print_failure(f"Devrait être 400, mais: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_validation_invalid_rating():
    """Test: Rating invalide rejeté"""
    print_test("Validation: Rating > 5")
    
    if not admin_token or not created_ids['place']:
        print_failure("Données manquantes")
        return False
    
    headers_auth = HEADERS.copy()
    headers_auth['Authorization'] = f'Bearer {admin_token}'
    
    review_data = {
        "text": "Test review",
        "rating": 10,
        "place_id": created_ids['place'],
        "user_id": created_ids['admin']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=headers_auth)
        
        if response.status_code == 400:
            print_success("Rating invalide rejeté")
            return True
        else:
            print_failure(f"Devrait être 400, mais: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


# ========== PUBLIC ACCESS TESTS ==========

def test_public_get_places():
    """Test: Accès public aux places"""
    print_test("GET places (public)")
    
    try:
        response = requests.get(f"{BASE_URL}/places/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"{len(data)} place(s) trouvé(s)")
            return True
        else:
            print_failure(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def test_public_get_amenities():
    """Test: Accès public aux amenities"""
    print_test("GET amenities (public)")
    
    try:
        response = requests.get(f"{BASE_URL}/amenities/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"{len(data)} amenity/amenities trouvée(s)")
            return True
        else:
            print_failure(f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {e}")
        return False


def print_summary():
    print_header("RÉSUMÉ DES TESTS")
    
    print(f"Tests exécutés : {tests_total}")
    print(f"{Fore.GREEN}Tests réussis  : {tests_passed} ✓{Style.RESET_ALL}")
    print(f"{Fore.RED}Tests échoués  : {tests_failed} ✗{Style.RESET_ALL}")
    
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"\nTaux de réussite : {success_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 TOUS LES TESTS SONT PASSÉS ! 🎉{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Ton projet Part 3 est fonctionnel !{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠ Certains tests ont échoué.{Style.RESET_ALL}")


def main():
    print_header("TEST COMPLET - HBnB Part 3")
    print_info("Vérification serveur Flask sur http://localhost:5000")
    
    try:
        requests.get(BASE_URL + "/users/", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}❌ ERREUR: Serveur Flask inaccessible !{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Lance: flask run{Style.RESET_ALL}\n")
        return
    
    # AUTHENTICATION
    print_header("SECTION 1: AUTHENTICATION")
    test_login_admin()
    test_create_regular_user()
    test_login_regular_user()
    
    # AMENITIES
    print_header("SECTION 2: AMENITIES (Admin only)")
    test_create_amenity_as_admin()
    test_create_amenity_as_user_forbidden()
    
    # PLACES
    print_header("SECTION 3: PLACES")
    test_create_place_as_user()
    test_user_cannot_create_place_for_others()
    test_admin_can_create_place_for_others()
    
    # REVIEWS
    print_header("SECTION 4: REVIEWS")
    test_create_review_as_admin()
    test_user_cannot_review_own_place()
    
    # VALIDATIONS
    print_header("SECTION 5: VALIDATIONS")
    test_validation_negative_price()
    test_validation_invalid_rating()
    
    # PUBLIC ACCESS
    print_header("SECTION 6: PUBLIC ACCESS")
    test_public_get_places()
    test_public_get_amenities()
    
    print_summary()


if __name__ == "__main__":
    main()
