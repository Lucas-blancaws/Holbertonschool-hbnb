#!/usr/bin/env python3
"""
Script de test complet pour les tâches 0 à 7 du projet HBnB Part 3
Exécuter avec : python3 test_tasks_0_to_7.py
"""

import requests
import json
import sys
from time import sleep

# Configuration
BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {"Content-Type": "application/json"}

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test(message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 TEST: {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_section(message):
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}{Colors.END}")

# Variables globales pour stocker les données des tests
test_data = {
    'admin_token': None,
    'user_token': None,
    'admin_id': None,
    'user_id': None,
    'place_id': None,
    'amenity_id': None,
    'review_id': None
}

def test_server_running():
    """Test 0: Vérifier que le serveur est accessible"""
    print_section("TÂCHE 0: Configuration et Application Factory")
    print_test("Vérification que le serveur Flask est accessible")
    try:
        response = requests.get(f"{BASE_URL}/users/", timeout=5)
        print_success(f"Serveur accessible (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print_error("Le serveur n'est pas accessible. Assurez-vous que 'python3 run.py' est lancé.")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False

def test_create_admin_user():
    """Test 1: Créer un utilisateur admin"""
    print_section("TÂCHE 1: Création d'utilisateur avec mot de passe hashé")
    print_test("Création d'un utilisateur administrateur")
    
    admin_data = {
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@test.com",
        "password": "admin123",
        "is_admin": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=admin_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            test_data['admin_id'] = data['id']
            print_success(f"Admin créé avec succès (ID: {data['id']})")
            
            # Vérifier que le password n'est PAS retourné
            if 'password' not in data:
                print_success("Le mot de passe n'est PAS retourné dans la réponse (sécurité OK)")
            else:
                print_error("SÉCURITÉ: Le mot de passe est retourné dans la réponse!")
            return True
        else:
            print_error(f"Échec création admin (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_create_regular_user():
    """Test 1b: Créer un utilisateur normal"""
    print_test("Création d'un utilisateur normal")
    
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "password": "user123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=HEADERS)
        
        if response.status_code == 201:
            data = response.json()
            test_data['user_id'] = data['id']
            print_success(f"Utilisateur créé avec succès (ID: {data['id']})")
            
            # Vérifier que le password n'est PAS retourné
            if 'password' not in data:
                print_success("Le mot de passe n'est PAS retourné dans la réponse")
            return True
        else:
            print_error(f"Échec création utilisateur (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_login_admin():
    """Test 2: Login et génération JWT pour admin"""
    print_section("TÂCHE 2: Authentification JWT")
    print_test("Connexion de l'administrateur")
    
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                test_data['admin_token'] = data['access_token']
                print_success("Token JWT admin obtenu avec succès")
                print_success(f"Token: {data['access_token'][:50]}...")
                
                # Vérifier que le token contient le claim is_admin
                print_test("Vérification du claim is_admin dans le token")
                import jwt as pyjwt
                try:
                    decoded = pyjwt.decode(data['access_token'], options={"verify_signature": False})
                    if decoded.get('is_admin') == True:
                        print_success("Le claim 'is_admin' est présent et vaut True")
                    else:
                        print_error(f"Le claim 'is_admin' vaut {decoded.get('is_admin')}")
                except:
                    print_warning("Impossible de décoder le token (pyjwt non installé?)")
                
                return True
            else:
                print_error("Pas de token dans la réponse")
                return False
        else:
            print_error(f"Échec login admin (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_login_user():
    """Test 2b: Login utilisateur normal"""
    print_test("Connexion de l'utilisateur normal")
    
    login_data = {
        "email": "john@test.com",
        "password": "user123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                test_data['user_token'] = data['access_token']
                print_success("Token JWT utilisateur obtenu avec succès")
                return True
        print_error(f"Échec login utilisateur (Status: {response.status_code})")
        return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_wrong_password():
    """Test 2c: Vérifier que le hash fonctionne (mauvais password)"""
    print_test("Tentative de connexion avec un mauvais mot de passe")
    
    login_data = {
        "email": "admin@test.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        
        if response.status_code == 401:
            print_success("Le mauvais mot de passe est bien rejeté (hash OK)")
            return True
        else:
            print_error(f"Le mauvais mot de passe n'est pas rejeté! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_protected_endpoint():
    """Test 2d: Accès à un endpoint protégé"""
    print_test("Accès au endpoint protégé avec le token")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/protected/protected", headers=auth_header)
        
        if response.status_code == 200:
            print_success("Accès autorisé au endpoint protégé avec JWT")
            return True
        else:
            print_error(f"Accès refusé (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_protected_without_token():
    """Test 2e: Vérifier qu'on ne peut pas accéder sans token"""
    print_test("Tentative d'accès au endpoint protégé SANS token")
    
    try:
        response = requests.get(f"{BASE_URL}/protected/protected", headers=HEADERS)
        
        if response.status_code in [401, 422]:
            print_success("Accès refusé sans token (protection JWT OK)")
            return True
        else:
            print_error(f"Accès autorisé sans token! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_create_place_authenticated():
    """Test 3: Créer un place en tant qu'utilisateur authentifié"""
    print_section("TÂCHE 3: Endpoints authentifiés")
    print_test("Création d'un place par l'utilisateur authentifié")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    place_data = {
        "title": "Belle maison",
        "description": "Maison avec jardin",
        "price": 100.0,
        "latitude": 45.5,
        "longitude": 2.5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/places/", json=place_data, headers=auth_header)
        
        if response.status_code == 201:
            data = response.json()
            test_data['place_id'] = data['id']
            print_success(f"Place créé avec succès (ID: {data['id']})")
            
            # Vérifier que l'owner_id est bien l'utilisateur connecté
            if data.get('owner_id') == test_data['user_id']:
                print_success("L'owner_id correspond bien à l'utilisateur connecté")
            else:
                print_warning(f"Owner ID: {data.get('owner_id')} vs User ID: {test_data['user_id']}")
            
            return True
        else:
            print_error(f"Échec création place (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_update_own_place():
    """Test 3b: Modifier son propre place"""
    print_test("Modification du place par son propriétaire")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "title": "Belle maison (modifiée)",
        "price": 120.0
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/places/{test_data['place_id']}",
            json=update_data,
            headers=auth_header
        )
        
        if response.status_code == 200:
            print_success("Place modifié avec succès par son propriétaire")
            return True
        else:
            print_error(f"Échec modification (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_create_review_authenticated():
    """Test 3c: Créer une review"""
    print_test("Création d'une review (admin review le place de user)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['admin_token']}",
        "Content-Type": "application/json"
    }
    
    review_data = {
        "text": "Très bel endroit!",
        "rating": 5,
        "place_id": test_data['place_id']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=auth_header)
        
        if response.status_code == 201:
            data = response.json()
            test_data['review_id'] = data['id']
            print_success(f"Review créée avec succès (ID: {data['id']})")
            return True
        else:
            print_error(f"Échec création review (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_cannot_review_own_place():
    """Test 3d: Vérifier qu'on ne peut pas reviewer son propre place"""
    print_test("Tentative de review de son propre place (doit échouer)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    review_data = {
        "text": "Mon propre place est super!",
        "rating": 5,
        "place_id": test_data['place_id']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=auth_header)
        
        if response.status_code == 400:
            print_success("Review de son propre place bien refusée")
            return True
        else:
            print_error(f"Review de son propre place autorisée! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_cannot_review_twice():
    """Test 3e: Vérifier qu'on ne peut pas reviewer 2 fois le même place"""
    print_test("Tentative de review multiple du même place (doit échouer)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['admin_token']}",
        "Content-Type": "application/json"
    }
    
    review_data = {
        "text": "Encore une review!",
        "rating": 4,
        "place_id": test_data['place_id']
    }
    
    try:
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data, headers=auth_header)
        
        if response.status_code == 400:
            print_success("Review multiple bien refusée")
            return True
        else:
            print_error(f"Review multiple autorisée! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_update_own_user():
    """Test 3f: Modifier ses propres infos utilisateur"""
    print_test("Modification de ses propres informations utilisateur")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "first_name": "Johnny"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/users/{test_data['user_id']}",
            json=update_data,
            headers=auth_header
        )
        
        if response.status_code == 200:
            print_success("Informations utilisateur modifiées avec succès")
            return True
        else:
            print_error(f"Échec modification (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_cannot_update_email():
    """Test 3g: Vérifier qu'un user ne peut pas modifier son email"""
    print_test("Tentative de modification d'email (doit échouer)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "email": "newemail@test.com"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/users/{test_data['user_id']}",
            json=update_data,
            headers=auth_header
        )
        
        if response.status_code == 400:
            print_success("Modification d'email bien refusée pour user normal")
            return True
        else:
            print_error(f"Modification d'email autorisée! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_admin_create_amenity():
    """Test 4: Admin crée une amenity"""
    print_section("TÂCHE 4: Endpoints administrateur")
    print_test("Création d'une amenity (admin uniquement)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['admin_token']}",
        "Content-Type": "application/json"
    }
    
    amenity_data = {
        "name": "WiFi"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/amenities/", json=amenity_data, headers=auth_header)
        
        if response.status_code == 201:
            data = response.json()
            test_data['amenity_id'] = data['id']
            print_success(f"Amenity créée avec succès (ID: {data['id']})")
            return True
        else:
            print_error(f"Échec création amenity (Status: {response.status_code})")
            print_error(f"Réponse: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_user_cannot_create_amenity():
    """Test 4b: User normal ne peut pas créer d'amenity"""
    print_test("Tentative de création d'amenity par user normal (doit échouer)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['user_token']}",
        "Content-Type": "application/json"
    }
    
    amenity_data = {
        "name": "Piscine"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/amenities/", json=amenity_data, headers=auth_header)
        
        if response.status_code == 403:
            print_success("Création d'amenity bien refusée pour user normal")
            return True
        else:
            print_error(f"Création d'amenity autorisée! (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_admin_modify_any_user():
    """Test 4c: Admin modifie n'importe quel utilisateur"""
    print_test("Modification d'un utilisateur par l'admin (email + password)")
    
    auth_header = {
        "Authorization": f"Bearer {test_data['admin_token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "email": "john.updated@test.com",
        "password": "newpassword123"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/users/{test_data['user_id']}",
            json=update_data,
            headers=auth_header
        )
        
        if response.status_code == 200:
            print_success("Admin a modifié l'utilisateur avec succès (email + password)")
            
            # Vérifier que le nouveau password fonctionne
            print_test("Vérification que le nouveau mot de passe fonctionne")
            login_data = {
                "email": "john.updated@test.com",
                "password": "newpassword123"
            }
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
            
            if login_response.status_code == 200:
                print_success("Nouveau mot de passe fonctionne (hash OK)")
                return True
            else:
                print_error("Nouveau mot de passe ne fonctionne pas")
                return False
        else:
            print_error(f"Échec modification par admin (Status: {response.status_code})")
            return False
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_database_persistence():
    """Test 5-7: Vérifier la persistance en base de données"""
    print_section("TÂCHES 5-7: Persistance SQLAlchemy")
    print_test("Vérification de la persistance en base de données")
    
    try:
        # Récupérer l'utilisateur
        response = requests.get(f"{BASE_URL}/users/{test_data['user_id']}")
        if response.status_code == 200:
            print_success("User récupéré depuis la base de données")
        else:
            print_error("Échec récupération user")
            return False
        
        # Récupérer le place
        response = requests.get(f"{BASE_URL}/places/{test_data['place_id']}")
        if response.status_code == 200:
            print_success("Place récupéré depuis la base de données")
        else:
            print_error("Échec récupération place")
            return False
        
        # Récupérer la review
        response = requests.get(f"{BASE_URL}/reviews/{test_data['review_id']}")
        if response.status_code == 200:
            print_success("Review récupérée depuis la base de données")
        else:
            print_error("Échec récupération review")
            return False
        
        # Récupérer l'amenity
        response = requests.get(f"{BASE_URL}/amenities/{test_data['amenity_id']}")
        if response.status_code == 200:
            print_success("Amenity récupérée depuis la base de données")
        else:
            print_error("Échec récupération amenity")
            return False
        
        print_success("Toutes les entités sont persistées correctement en base de données")
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def test_get_all_entities():
    """Test supplémentaire: Récupérer toutes les entités"""
    print_test("Récupération de toutes les entités (GET all)")
    
    try:
        # Users
        response = requests.get(f"{BASE_URL}/users/")
        if response.status_code == 200 and len(response.json()) >= 2:
            print_success(f"Liste des users récupérée ({len(response.json())} users)")
        
        # Places
        response = requests.get(f"{BASE_URL}/places/")
        if response.status_code == 200 and len(response.json()) >= 1:
            print_success(f"Liste des places récupérée ({len(response.json())} places)")
        
        # Reviews
        response = requests.get(f"{BASE_URL}/reviews/")
        if response.status_code == 200 and len(response.json()) >= 1:
            print_success(f"Liste des reviews récupérée ({len(response.json())} reviews)")
        
        # Amenities
        response = requests.get(f"{BASE_URL}/amenities/")
        if response.status_code == 200 and len(response.json()) >= 1:
            print_success(f"Liste des amenities récupérée ({len(response.json())} amenities)")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False

def cleanup():
    """Nettoyage optionnel (commenté par défaut)"""
    print_section("NETTOYAGE (optionnel)")
    print_warning("Les données de test restent en base pour inspection manuelle")
    print_warning("Pour nettoyer: supprimez le fichier development.db et relancez l'app")

def main():
    """Fonction principale"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print(f"  TEST COMPLET - HBNB PART 3 - TÂCHES 0 À 7")
    print(f"{'='*70}{Colors.END}\n")
    
    results = []
    
    # Tâche 0
    if not test_server_running():
        print_error("\n❌ Le serveur n'est pas accessible. Arrêt des tests.")
        sys.exit(1)
    
    # Tâche 1
    results.append(("Création admin", test_create_admin_user()))
    results.append(("Création user", test_create_regular_user()))
    
    # Tâche 2
    results.append(("Login admin", test_login_admin()))
    results.append(("Login user", test_login_user()))
    results.append(("Mauvais password", test_wrong_password()))
    results.append(("Endpoint protégé", test_protected_endpoint()))
    results.append(("Sans token", test_protected_without_token()))
    
    # Tâche 3
    results.append(("Création place", test_create_place_authenticated()))
    results.append(("Modification place", test_update_own_place()))
    results.append(("Création review", test_create_review_authenticated()))
    results.append(("Review propre place", test_cannot_review_own_place()))
    results.append(("Review multiple", test_cannot_review_twice()))
    results.append(("Modification user", test_update_own_user()))
    results.append(("Modification email", test_cannot_update_email()))
    
    # Tâche 4
    results.append(("Admin crée amenity", test_admin_create_amenity()))
    results.append(("User crée amenity", test_user_cannot_create_amenity()))
    results.append(("Admin modifie user", test_admin_modify_any_user()))
    
    # Tâches 5-7
    results.append(("Persistance DB", test_database_persistence()))
    results.append(("GET all entities", test_get_all_entities()))
    
    # Nettoyage
    cleanup()
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {name}")
    
    print(f"\n{Colors.BOLD}Résultat: {passed}/{total} tests réussis{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TOUS LES TESTS SONT PASSÉS ! Vous êtes prêt pour la tâche 8 !{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {total - passed} test(s) en échec. Vérifiez les corrections.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
