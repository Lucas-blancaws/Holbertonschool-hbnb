#!/usr/bin/env python3
"""
Script de test pour valider le mapping des entités Place, Review et Amenity
Auteur: Test automatique pour Holberton School - HBnB Project
"""

import requests
import json
from colorama import Fore, Style, init

# Initialise colorama pour les couleurs dans le terminal
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# ⚠️ CONFIGURATION AUTHENTIFICATION
# Si ton API nécessite un token JWT, décommente et configure ci-dessous:
USE_AUTH = True  # Mettre True si tu corriges la route de login
AUTH_TOKEN = None  # Sera rempli après le login

# Compteurs de tests
tests_passed = 0
tests_failed = 0
tests_total = 0

# Stockage des IDs créés
created_ids = {
    'user': None,
    'place': None,
    'review': None,
    'amenity': None
}


def login_and_get_token():
    """Se connecter et obtenir un token JWT si nécessaire"""
    if not USE_AUTH:
        return True
    
    print_info("Tentative de connexion pour obtenir un token JWT...")
    
    # Essayer de se connecter avec des credentials par défaut
    # MODIFIE CES VALEURS avec un user admin existant dans ta base
    login_data = {
        "email": "admin@hbnb.io",
        "password": "admin1234"
    }
    
    try:
        print_info(f"Tentative de login sur: {BASE_URL}/auth/login")
        print_info(f"Avec email: {login_data['email']}")
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS, timeout=5)
        
        print_info(f"Status code reçu: {response.status_code}")
        print_info(f"Réponse brute: {response.text[:200] if response.text else 'Vide'}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print_info(f"JSON parsé: {data}")
                
                # Essayer différentes clés possibles pour le token
                token = data.get('access_token') or data.get('token') or data.get('jwt') or data.get('auth_token')
                
                if token:
                    global AUTH_TOKEN
                    AUTH_TOKEN = token
                    HEADERS['Authorization'] = f'Bearer {token}'
                    print_success("Token JWT obtenu avec succès")
                    print_info(f"Token (premiers chars): {token[:20]}...")
                    return True
                else:
                    print_failure("Token non trouvé dans la réponse")
                    print_info("Clés disponibles: " + str(list(data.keys())))
                    return False
            except json.JSONDecodeError:
                print_failure("La réponse n'est pas du JSON valide")
                return False
        elif response.status_code == 401:
            print_failure("Login échoué - Mauvais credentials (401)")
            print_info("Vérifie que le mot de passe est bien 'admin1234' pour admin@hbnb.io")
            return False
        else:
            print_failure(f"Login échoué - Status code: {response.status_code}")
            print_info(f"Réponse complète: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print_failure("Timeout lors du login (>5 secondes)")
        return False
    except Exception as e:
        print_failure(f"Exception lors du login: {str(e)}")
        import traceback
        print_info(traceback.format_exc())
        return False


def print_header(title):
    """Affiche un en-tête de section"""
    print(f"\n{'='*70}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(70)}")
    print(f"{'='*70}\n")


def print_test(test_name):
    """Affiche le nom du test en cours"""
    global tests_total
    tests_total += 1
    print(f"{Fore.YELLOW}[TEST {tests_total}] {test_name}...", end=" ")


def print_success(message=""):
    """Affiche un succès"""
    global tests_passed
    tests_passed += 1
    print(f"{Fore.GREEN}✓ PASSED{Style.RESET_ALL} {message}")


def print_failure(message=""):
    """Affiche un échec"""
    global tests_failed
    tests_failed += 1
    print(f"{Fore.RED}✗ FAILED{Style.RESET_ALL} {message}")


def print_info(message):
    """Affiche une information"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def test_create_user():
    """Test: Créer un User (prérequis pour Place et Review)"""
    print_test("Création d'un User")
    
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.test{tests_total}@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['user'] = data.get('id')
            
            # Vérifier que tous les champs sont présents
            required_fields = ['id', 'first_name', 'last_name', 'email']
            if all(field in data for field in required_fields):
                print_success(f"User créé avec ID: {created_ids['user'][:8]}...")
                return True
            else:
                print_failure("Champs manquants dans la réponse")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            print_info(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_create_amenity():
    """Test: Créer une Amenity"""
    print_test("Création d'une Amenity")
    
    amenity_data = {"name": "WiFi"}
    
    try:
        response = requests.post(f"{BASE_URL}/amenities/", json=amenity_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['amenity'] = data.get('id')
            
            if 'id' in data and 'name' in data and data['name'] == "WiFi":
                print_success(f"Amenity créée avec ID: {created_ids['amenity'][:8]}...")
                return True
            else:
                print_failure("Données incorrectes dans la réponse")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_create_place():
    """Test: Créer un Place avec owner_id"""
    print_test("Création d'un Place")
    
    if not created_ids['user']:
        print_failure("Aucun User disponible (prérequis)")
        return False
    
    place_data = {
        "title": "Cozy Apartment in Paris",
        "description": "Beautiful apartment in the city center",
        "price": 120.50,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['place'] = data.get('id')
            
            # Vérifier les champs obligatoires
            required_fields = ['id', 'title', 'price', 'latitude', 'longitude', 'owner_id']
            if all(field in data for field in required_fields):
                print_success(f"Place créé avec ID: {created_ids['place'][:8]}...")
                return True
            else:
                print_failure("Champs manquants dans la réponse")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            print_info(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_create_review():
    """Test: Créer une Review avec place_id et user_id"""
    print_test("Création d'une Review")
    
    if not created_ids['place'] or not created_ids['user']:
        print_failure("Place ou User manquant (prérequis)")
        return False
    
    review_data = {
        "text": "Amazing place! Very clean and comfortable.",
        "rating": 5,
        "place_id": created_ids['place'],
        "user_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            created_ids['review'] = data.get('id')
            
            required_fields = ['id', 'text', 'rating', 'place_id', 'user_id']
            if all(field in data for field in required_fields):
                print_success(f"Review créée avec ID: {created_ids['review'][:8]}...")
                return True
            else:
                print_failure("Champs manquants dans la réponse")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            print_info(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_get_all_places():
    """Test: Récupérer tous les Places (READ)"""
    print_test("Récupération de tous les Places")
    
    try:
        response = requests.get(f"{BASE_URL}/places/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_success(f"{len(data)} place(s) trouvé(s)")
                return True
            else:
                print_failure("Aucun place retourné")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_get_place_by_id():
    """Test: Récupérer un Place par ID (READ)"""
    print_test("Récupération d'un Place par ID")
    
    if not created_ids['place']:
        print_failure("Aucun Place disponible")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/places/{created_ids['place']}", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('id') == created_ids['place']:
                print_success(f"Place récupéré: {data.get('title')}")
                return True
            else:
                print_failure("ID ne correspond pas")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_get_all_reviews():
    """Test: Récupérer toutes les Reviews (READ)"""
    print_test("Récupération de toutes les Reviews")
    
    try:
        response = requests.get(f"{BASE_URL}/reviews/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_success(f"{len(data)} review(s) trouvée(s)")
                return True
            else:
                print_failure("Aucune review retournée")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_get_all_amenities():
    """Test: Récupérer toutes les Amenities (READ)"""
    print_test("Récupération de toutes les Amenities")
    
    try:
        response = requests.get(f"{BASE_URL}/amenities/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print_success(f"{len(data)} amenity/amenities trouvée(s)")
                return True
            else:
                print_failure("Aucune amenity retournée")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_update_place():
    """Test: Mettre à jour un Place (UPDATE)"""
    print_test("Mise à jour d'un Place")
    
    if not created_ids['place']:
        print_failure("Aucun Place disponible")
        return False
    
    update_data = {
        "title": "Updated Cozy Apartment",
        "price": 150.0
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/places/{created_ids['place']}", 
            json=update_data, 
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('title') == "Updated Cozy Apartment" and data.get('price') == 150.0:
                print_success("Place mis à jour avec succès")
                return True
            else:
                print_failure("Données non mises à jour correctement")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_update_review():
    """Test: Mettre à jour une Review (UPDATE)"""
    print_test("Mise à jour d'une Review")
    
    if not created_ids['review']:
        print_failure("Aucune Review disponible")
        return False
    
    update_data = {
        "text": "Updated: Amazing place! Highly recommend.",
        "rating": 5
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/reviews/{created_ids['review']}", 
            json=update_data, 
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Updated" in data.get('text', ''):
                print_success("Review mise à jour avec succès")
                return True
            else:
                print_failure("Données non mises à jour correctement")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_update_amenity():
    """Test: Mettre à jour une Amenity (UPDATE)"""
    print_test("Mise à jour d'une Amenity")
    
    if not created_ids['amenity']:
        print_failure("Aucune Amenity disponible")
        return False
    
    update_data = {"name": "WiFi High Speed"}
    
    try:
        response = requests.put(
            f"{BASE_URL}/amenities/{created_ids['amenity']}", 
            json=update_data, 
            headers=HEADERS
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('name') == "WiFi High Speed":
                print_success("Amenity mise à jour avec succès")
                return True
            else:
                print_failure("Données non mises à jour correctement")
                return False
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_delete_review():
    """Test: Supprimer une Review (DELETE)"""
    print_test("Suppression d'une Review")
    
    if not created_ids['review']:
        print_failure("Aucune Review disponible")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/reviews/{created_ids['review']}", headers=HEADERS)
        
        if response.status_code == 200 or response.status_code == 204:
            print_success("Review supprimée avec succès")
            return True
        else:
            print_failure(f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_validation_negative_price():
    """Test: Validation - Prix négatif rejeté"""
    print_test("Validation: Prix négatif doit être rejeté")
    
    if not created_ids['user']:
        print_failure("Aucun User disponible")
        return False
    
    invalid_place = {
        "title": "Invalid Place",
        "price": -50.0,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "owner_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=invalid_place, headers=HEADERS)
        
        if response.status_code == 400:
            print_success("Prix négatif correctement rejeté")
            return True
        else:
            print_failure(f"Devrait retourner 400, mais a retourné {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_validation_invalid_rating():
    """Test: Validation - Rating invalide rejeté"""
    print_test("Validation: Rating > 5 doit être rejeté")
    
    if not created_ids['place'] or not created_ids['user']:
        print_failure("Place ou User manquant")
        return False
    
    invalid_review = {
        "text": "Test review",
        "rating": 10,
        "place_id": created_ids['place'],
        "user_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=invalid_review, headers=HEADERS)
        
        if response.status_code == 400:
            print_success("Rating invalide correctement rejeté")
            return True
        else:
            print_failure(f"Devrait retourner 400, mais a retourné {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def test_validation_invalid_latitude():
    """Test: Validation - Latitude invalide rejetée"""
    print_test("Validation: Latitude > 90 doit être rejetée")
    
    if not created_ids['user']:
        print_failure("Aucun User disponible")
        return False
    
    invalid_place = {
        "title": "Invalid Place",
        "price": 100.0,
        "latitude": 95.0,
        "longitude": 2.3522,
        "owner_id": created_ids['user']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=invalid_place, headers=HEADERS)
        
        if response.status_code == 400:
            print_success("Latitude invalide correctement rejetée")
            return True
        else:
            print_failure(f"Devrait retourner 400, mais a retourné {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Exception: {str(e)}")
        return False


def print_summary():
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DES TESTS")
    
    print(f"Tests exécutés : {tests_total}")
    print(f"{Fore.GREEN}Tests réussis  : {tests_passed} ✓{Style.RESET_ALL}")
    print(f"{Fore.RED}Tests échoués  : {tests_failed} ✗{Style.RESET_ALL}")
    
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"\nTaux de réussite : {success_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 TOUS LES TESTS SONT PASSÉS ! 🎉{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Ton exercice est validé !{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠ Certains tests ont échoué. Vérifie les erreurs ci-dessus.{Style.RESET_ALL}")


def main():
    """Fonction principale"""
    print_header("TEST AUTOMATIQUE - MAPPING ENTITIES (Place, Review, Amenity)")
    print_info("Vérification que le serveur Flask est démarré sur http://localhost:5000")
    
    try:
        response = requests.get(BASE_URL + "/users/", headers=HEADERS, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}❌ ERREUR: Le serveur Flask n'est pas accessible !{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Assure-toi que Flask est démarré avec: flask run{Style.RESET_ALL}\n")
        return
    
    # Authentification si nécessaire
    if USE_AUTH:
        if not login_and_get_token():
            print(f"\n{Fore.RED}❌ ERREUR: Impossible de s'authentifier !{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}OPTIONS:{Style.RESET_ALL}")
            print("1. Crée un compte admin dans ta base de données")
            print("2. Modifie login_data dans le script avec tes credentials")
            print("3. Désactive l'auth: USE_AUTH = False (si ton API le permet)")
            return
    
    # Section 1: CREATE Tests
    print_header("SECTION 1: TESTS CREATE (Création)")
    test_create_user()
    test_create_amenity()
    test_create_place()
    test_create_review()
    
    # Section 2: READ Tests
    print_header("SECTION 2: TESTS READ (Lecture)")
    test_get_all_places()
    test_get_place_by_id()
    test_get_all_reviews()
    test_get_all_amenities()
    
    # Section 3: UPDATE Tests
    print_header("SECTION 3: TESTS UPDATE (Mise à jour)")
    test_update_place()
    test_update_review()
    test_update_amenity()
    
    # Section 4: DELETE Tests
    print_header("SECTION 4: TESTS DELETE (Suppression)")
    test_delete_review()
    
    # Section 5: VALIDATION Tests
    print_header("SECTION 5: TESTS VALIDATION")
    test_validation_negative_price()
    test_validation_invalid_rating()
    test_validation_invalid_latitude()
    
    # Afficher le résumé
    print_summary()


if __name__ == "__main__":
    main()