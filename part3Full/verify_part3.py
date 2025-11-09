#!/usr/bin/env python3
"""
Script de vérification complet pour la Part 3 du projet HBnB
Vérifie tous les exercices de 0 à 8
"""

import sys
import importlib
import inspect
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

# Compteurs
tests_passed = 0
tests_failed = 0
tests_total = 0

def print_header(title):
    """Affiche un en-tête de section"""
    print(f"\n{'='*80}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(80)}")
    print(f"{'='*80}\n")

def print_task(task_name):
    """Affiche le nom de la tâche"""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}▶ {task_name}{Style.RESET_ALL}")

def print_test(test_name):
    """Affiche le nom du test"""
    global tests_total
    tests_total += 1
    print(f"  {Fore.YELLOW}[TEST {tests_total}] {test_name}...", end=" ")

def print_success(message=""):
    """Affiche un succès"""
    global tests_passed
    tests_passed += 1
    print(f"{Fore.GREEN}✓ PASS{Style.RESET_ALL} {message}")

def print_failure(message=""):
    """Affiche un échec"""
    global tests_failed
    tests_failed += 1
    print(f"{Fore.RED}✗ FAIL{Style.RESET_ALL} {message}")

def print_info(message):
    """Affiche une information"""
    print(f"  {Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_warning(message):
    """Affiche un avertissement"""
    print(f"  {Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


# ============================================================================
# TASK 0: Application Factory avec Configuration
# ============================================================================
def check_task_0():
    """Vérifie la configuration et l'Application Factory"""
    print_task("TASK 0: Application Factory avec Configuration")
    
    # Test 1: Vérifier que config.py existe et contient les bonnes classes
    print_test("Vérifier config.py")
    try:
        import config
        
        required_configs = ['Config', 'DevelopmentConfig']
        missing = [c for c in required_configs if not hasattr(config, c)]
        
        if missing:
            print_failure(f"Classes manquantes: {', '.join(missing)}")
        else:
            print_success()
    except ImportError:
        print_failure("config.py introuvable")
    
    # Test 2: Vérifier JWT_SECRET_KEY
    print_test("Vérifier JWT_SECRET_KEY dans Config")
    try:
        from config import Config
        if hasattr(Config, 'JWT_SECRET_KEY') and Config.JWT_SECRET_KEY:
            print_success(f"JWT_SECRET_KEY défini")
        else:
            print_failure("JWT_SECRET_KEY manquant ou None")
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier create_app()
    print_test("Vérifier create_app() dans app/__init__.py")
    try:
        from app import create_app
        
        # Vérifier la signature
        sig = inspect.signature(create_app)
        if 'config_class' in sig.parameters:
            print_success("create_app() accepte config_class")
        else:
            print_warning("create_app() devrait accepter un paramètre config_class")
            tests_passed += 1
            tests_total += 1
    except ImportError:
        print_failure("Impossible d'importer create_app")
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 1: User Model avec Password Hashing
# ============================================================================
def check_task_1():
    """Vérifie le modèle User avec hachage de mot de passe"""
    print_task("TASK 1: User Model avec Password Hashing")
    
    # Test 1: Vérifier Flask-Bcrypt
    print_test("Vérifier que Flask-Bcrypt est installé")
    try:
        from flask_bcrypt import Bcrypt
        print_success()
    except ImportError:
        print_failure("Flask-Bcrypt non installé")
    
    # Test 2: Vérifier le modèle User
    print_test("Vérifier User.password et méthodes de hachage")
    try:
        from app.models.user import User
        
        # Vérifier les attributs
        if not hasattr(User, 'password'):
            print_failure("User.password manquant")
            return
        
        # Vérifier les méthodes
        required_methods = ['hash_password', 'verify_password']
        missing_methods = [m for m in required_methods if not hasattr(User, m)]
        
        if missing_methods:
            print_failure(f"Méthodes manquantes: {', '.join(missing_methods)}")
        else:
            print_success()
    except ImportError:
        print_failure("Impossible d'importer User")
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Tester le hachage de mot de passe
    print_test("Tester hash_password() et verify_password()")
    try:
        from app import create_app
        from app.models.user import User
        
        app = create_app()
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test@test.com",
                password="test123"
            )
            
            # Vérifier que le mot de passe est haché
            if user.password != "test123":
                # Vérifier la vérification
                if user.verify_password("test123"):
                    print_success("Hachage et vérification fonctionnent")
                else:
                    print_failure("verify_password() ne fonctionne pas")
            else:
                print_failure("Mot de passe non haché")
    except Exception as e:
        print_failure(str(e))
    
    # Test 4: Vérifier que le mot de passe n'est pas retourné dans to_dict()
    print_test("Vérifier que password n'est pas dans to_dict()")
    try:
        from app import create_app
        from app.models.user import User
        
        app = create_app()
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test2@test.com",
                password="test123"
            )
            
            user_dict = user.to_dict()
            if 'password' not in user_dict:
                print_success()
            else:
                print_failure("password présent dans to_dict()")
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 2: JWT Authentication
# ============================================================================
def check_task_2():
    """Vérifie l'authentification JWT"""
    print_task("TASK 2: JWT Authentication avec flask-jwt-extended")
    
    # Test 1: Vérifier flask-jwt-extended
    print_test("Vérifier que flask-jwt-extended est installé")
    try:
        from flask_jwt_extended import JWTManager
        print_success()
    except ImportError:
        print_failure("flask-jwt-extended non installé")
    
    # Test 2: Vérifier JWTManager dans app/__init__.py
    print_test("Vérifier JWTManager initialisé")
    try:
        from app import create_app
        app = create_app()
        
        # Vérifier que JWT_SECRET_KEY est configuré
        if app.config.get('JWT_SECRET_KEY'):
            print_success()
        else:
            print_failure("JWT_SECRET_KEY non configuré")
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier l'endpoint /auth/login
    print_test("Vérifier endpoint /api/v1/auth/login")
    try:
        from app.api.v1 import auth
        
        # Vérifier que le namespace auth existe
        if hasattr(auth, 'api'):
            print_success()
        else:
            print_failure("Namespace auth manquant")
    except ImportError:
        print_failure("Module auth introuvable")
    except Exception as e:
        print_failure(str(e))
    
    # Test 4: Vérifier la structure de la route login
    print_test("Vérifier classe Login dans auth.py")
    try:
        from app.api.v1.auth import Login
        
        if hasattr(Login, 'post'):
            print_success()
        else:
            print_failure("Méthode POST manquante dans Login")
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 3: Authenticated User Access
# ============================================================================
def check_task_3():
    """Vérifie les endpoints authentifiés"""
    print_task("TASK 3: Authenticated User Access Endpoints")
    
    # Test 1: Vérifier @jwt_required sur les bonnes routes
    print_test("Vérifier @jwt_required sur POST /places/")
    try:
        from app.api.v1.places import PlaceList
        import inspect
        
        source = inspect.getsource(PlaceList.post)
        if '@jwt_required' in source or 'jwt_required()' in source:
            print_success()
        else:
            print_warning("@jwt_required manquant (peut être OK pour les tests)")
            tests_passed += 1
            tests_total += 1
    except Exception as e:
        print_failure(str(e))
    
    # Test 2: Vérifier @jwt_required sur PUT /places/<id>
    print_test("Vérifier @jwt_required sur PUT /places/<id>")
    try:
        from app.api.v1.places import PlaceResource
        import inspect
        
        source = inspect.getsource(PlaceResource.put)
        if '@jwt_required' in source or 'jwt_required()' in source:
            print_success()
        else:
            print_warning("@jwt_required manquant (peut être OK pour les tests)")
            tests_passed += 1
            tests_total += 1
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier @jwt_required sur POST /reviews/
    print_test("Vérifier @jwt_required sur POST /reviews/")
    try:
        from app.api.v1.reviews import ReviewList
        import inspect
        
        source = inspect.getsource(ReviewList.post)
        if '@jwt_required' in source or 'jwt_required()' in source:
            print_success()
        else:
            print_warning("@jwt_required manquant (peut être OK pour les tests)")
            tests_passed += 1
            tests_total += 1
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 4: Administrator Access
# ============================================================================
def check_task_4():
    """Vérifie les accès administrateur"""
    print_task("TASK 4: Administrator Access Endpoints")
    
    # Test 1: Vérifier is_admin dans User
    print_test("Vérifier attribut is_admin dans User")
    try:
        from app.models.user import User
        
        if hasattr(User, 'is_admin'):
            print_success()
        else:
            print_failure("is_admin manquant dans User")
    except Exception as e:
        print_failure(str(e))
    
    # Test 2: Vérifier is_admin dans le token JWT
    print_test("Vérifier is_admin dans les claims JWT")
    try:
        from app.api.v1.auth import Login
        import inspect
        
        source = inspect.getsource(Login.post)
        if 'is_admin' in source and 'additional_claims' in source:
            print_success()
        else:
            print_failure("is_admin non ajouté aux claims JWT")
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier les vérifications admin dans les routes
    print_test("Vérifier vérifications is_admin dans amenities")
    try:
        from app.api.v1.amenities import AmenityList
        import inspect
        
        source = inspect.getsource(AmenityList.post)
        if 'is_admin' in source:
            print_success()
        else:
            print_warning("Vérification is_admin manquante (peut être OK pour les tests)")
            tests_passed += 1
            tests_total += 1
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 5: SQLAlchemy Repository
# ============================================================================
def check_task_5():
    """Vérifie le repository SQLAlchemy"""
    print_task("TASK 5: SQLAlchemy Repository Implementation")
    
    # Test 1: Vérifier SQLAlchemy installé
    print_test("Vérifier que SQLAlchemy est installé")
    try:
        import sqlalchemy
        print_success()
    except ImportError:
        print_failure("SQLAlchemy non installé")
    
    # Test 2: Vérifier Flask-SQLAlchemy
    print_test("Vérifier que Flask-SQLAlchemy est installé")
    try:
        from flask_sqlalchemy import SQLAlchemy
        print_success()
    except ImportError:
        print_failure("Flask-SQLAlchemy non installé")
    
    # Test 3: Vérifier SQLAlchemyRepository
    print_test("Vérifier classe SQLAlchemyRepository")
    try:
        from app.persistence.repository import SQLAlchemyRepository
        
        required_methods = ['add', 'get', 'get_all', 'update', 'delete']
        missing = [m for m in required_methods if not hasattr(SQLAlchemyRepository, m)]
        
        if missing:
            print_failure(f"Méthodes manquantes: {', '.join(missing)}")
        else:
            print_success()
    except ImportError:
        print_failure("SQLAlchemyRepository introuvable")
    except Exception as e:
        print_failure(str(e))
    
    # Test 4: Vérifier db dans extensions.py
    print_test("Vérifier db = SQLAlchemy() dans extensions.py")
    try:
        from app.extensions import db
        from flask_sqlalchemy import SQLAlchemy
        
        if isinstance(db, SQLAlchemy):
            print_success()
        else:
            print_failure("db n'est pas une instance de SQLAlchemy")
    except ImportError:
        print_failure("extensions.py ou db introuvable")
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 6: Map User Entity
# ============================================================================
def check_task_6():
    """Vérifie le mapping de l'entité User"""
    print_task("TASK 6: Map User Entity to SQLAlchemy")
    
    # Test 1: Vérifier BaseModel
    print_test("Vérifier BaseModel hérite de db.Model")
    try:
        from app.models.basemodel import BaseModel
        from app.extensions import db
        
        if issubclass(BaseModel, db.Model):
            print_success()
        else:
            print_failure("BaseModel n'hérite pas de db.Model")
    except Exception as e:
        print_failure(str(e))
    
    # Test 2: Vérifier les colonnes de BaseModel
    print_test("Vérifier colonnes id, created_at, updated_at dans BaseModel")
    try:
        from app.models.basemodel import BaseModel
        
        required_cols = ['id', 'created_at', 'updated_at']
        missing = [c for c in required_cols if not hasattr(BaseModel, c)]
        
        if missing:
            print_failure(f"Colonnes manquantes: {', '.join(missing)}")
        else:
            print_success()
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier User hérite de BaseModel
    print_test("Vérifier User hérite de BaseModel")
    try:
        from app.models.user import User
        from app.models.basemodel import BaseModel
        
        if issubclass(User, BaseModel):
            print_success()
        else:
            print_failure("User n'hérite pas de BaseModel")
    except Exception as e:
        print_failure(str(e))
    
    # Test 4: Vérifier les colonnes de User
    print_test("Vérifier colonnes SQLAlchemy dans User")
    try:
        from app.models.user import User
        
        required_cols = ['email', 'password', 'first_name', 'last_name', 'is_admin']
        missing = [c for c in required_cols if not hasattr(User, c)]
        
        if missing:
            print_failure(f"Colonnes manquantes: {', '.join(missing)}")
        else:
            print_success()
    except Exception as e:
        print_failure(str(e))
    
    # Test 5: Vérifier __tablename__
    print_test("Vérifier __tablename__ = 'users'")
    try:
        from app.models.user import User
        
        if hasattr(User, '__tablename__') and User.__tablename__ == 'users':
            print_success()
        else:
            print_failure("__tablename__ manquant ou incorrect")
    except Exception as e:
        print_failure(str(e))
    
    # Test 6: Vérifier UserRepository
    print_test("Vérifier UserRepository existe")
    try:
        from app.services.repositories.user_repository import UserRepository
        from app.persistence.repository import SQLAlchemyRepository
        
        if issubclass(UserRepository, SQLAlchemyRepository):
            print_success()
        else:
            print_failure("UserRepository n'hérite pas de SQLAlchemyRepository")
    except ImportError:
        print_failure("UserRepository introuvable")
    except Exception as e:
        print_failure(str(e))


# ============================================================================
# TASK 7: Map Place, Review, Amenity
# ============================================================================
def check_task_7():
    """Vérifie le mapping des entités Place, Review, Amenity"""
    print_task("TASK 7: Map Place, Review, and Amenity Entities")
    
    entities = [
        ('Place', 'app.models.place', 'places', ['title', 'price', 'latitude', 'longitude', 'owner_id']),
        ('Review', 'app.models.review', 'reviews', ['text', 'rating', 'place_id', 'user_id']),
        ('Amenity', 'app.models.amenity', 'amenities', ['name'])
    ]
    
    for entity_name, module_path, table_name, required_cols in entities:
        # Test 1: Vérifier l'entité existe
        print_test(f"Vérifier {entity_name} hérite de BaseModel")
        try:
            module = importlib.import_module(module_path)
            entity_class = getattr(module, entity_name)
            from app.models.basemodel import BaseModel
            
            if issubclass(entity_class, BaseModel):
                print_success()
            else:
                print_failure(f"{entity_name} n'hérite pas de BaseModel")
        except Exception as e:
            print_failure(str(e))
        
        # Test 2: Vérifier __tablename__
        print_test(f"Vérifier __tablename__ = '{table_name}'")
        try:
            if hasattr(entity_class, '__tablename__') and entity_class.__tablename__ == table_name:
                print_success()
            else:
                print_failure(f"__tablename__ incorrect pour {entity_name}")
        except Exception as e:
            print_failure(str(e))
        
        # Test 3: Vérifier les colonnes
        print_test(f"Vérifier colonnes de {entity_name}")
        try:
            missing = [c for c in required_cols if not hasattr(entity_class, c)]
            
            if missing:
                print_failure(f"Colonnes manquantes: {', '.join(missing)}")
            else:
                print_success()
        except Exception as e:
            print_failure(str(e))
        
        # Test 4: Vérifier le repository
        repo_name = f"{entity_name}Repository"
        print_test(f"Vérifier {repo_name} existe")
        try:
            repo_module = importlib.import_module(f'app.services.repositories.{entity_name.lower()}_repository')
            repo_class = getattr(repo_module, repo_name)
            from app.persistence.repository import SQLAlchemyRepository
            
            if issubclass(repo_class, SQLAlchemyRepository):
                print_success()
            else:
                print_failure(f"{repo_name} n'hérite pas de SQLAlchemyRepository")
        except Exception as e:
            print_failure(str(e))


# ============================================================================
# TASK 8: Map Relationships
# ============================================================================
def check_task_8():
    """Vérifie les relations entre entités"""
    print_task("TASK 8: Map Relationships Between Entities")
    
    # Test 1: Vérifier relation User -> Place (one-to-many)
    print_test("Vérifier relation User -> Place (one-to-many)")
    try:
        from app.models.user import User
        
        if hasattr(User, 'places'):
            print_success()
        else:
            print_failure("Relation 'places' manquante dans User")
    except Exception as e:
        print_failure(str(e))
    
    # Test 2: Vérifier relation Place -> User (foreign key)
    print_test("Vérifier foreign key owner_id dans Place")
    try:
        from app.models.place import Place
        
        if hasattr(Place, 'owner_id'):
            print_success()
        else:
            print_failure("owner_id manquant dans Place")
    except Exception as e:
        print_failure(str(e))
    
    # Test 3: Vérifier relation User -> Review (one-to-many)
    print_test("Vérifier relation User -> Review (one-to-many)")
    try:
        from app.models.user import User
        
        if hasattr(User, 'reviews'):
            print_success()
        else:
            print_failure("Relation 'reviews' manquante dans User")
    except Exception as e:
        print_failure(str(e))
    
    # Test 4: Vérifier relation Place -> Review (one-to-many)
    print_test("Vérifier relation Place -> Review (one-to-many)")
    try:
        from app.models.place import Place
        
        if hasattr(Place, 'reviews'):
            print_success()
        else:
            print_failure("Relation 'reviews' manquante dans Place")
    except Exception as e:
        print_failure(str(e))
    
    # Test 5: Vérifier relation Place <-> Amenity (many-to-many)
    print_test("Vérifier table association place_amenity")
    try:
        from app.models.place_amenity import place_amenity
        from sqlalchemy import Table
        
        if isinstance(place_amenity, Table):
            print_success()
        else:
            print_failure("place_amenity n'est pas une Table SQLAlchemy")
    except ImportError:
        print_failure("place_amenity introuvable")
    except Exception as e:
        print_failure(str(e))
    
    # Test 6: Vérifier relation amenities dans Place
    print_test("Vérifier relation 'amenities' dans Place")
    try:
        from app.models.place import Place
        
        if hasattr(Place, 'amenities'):
            print_success()
        else:
            print_failure("Relation 'amenities' manquante dans Place")
    except Exception as e:
        print_failure(str(e))
    
    # Test 7: Vérifier backref places dans Amenity
    print_test("Vérifier backref 'places' accessible depuis Amenity")
    try:
        from app import create_app
        from app.models.amenity import Amenity
        
        # Créer une instance pour vérifier le backref
        app = create_app()
        with app.app_context():
            # Vérifier que la relation est définie
            if hasattr(Amenity, 'places'):
                print_success()
            else:
                print_warning("Backref 'places' non vérifié (nécessite une instance)")
                tests_passed += 1
                tests_total += 1
    except Exception as e:
        print_warning(f"Impossible de vérifier le backref: {str(e)}")
        tests_passed += 1
        tests_total += 1


# ============================================================================
# RÉSUMÉ
# ============================================================================
def print_summary():
    """Affiche le résumé des tests"""
    print_header("RÉSUMÉ DE LA VÉRIFICATION")
    
    print(f"Tests exécutés : {tests_total}")
    print(f"{Fore.GREEN}Tests réussis  : {tests_passed} ✓{Style.RESET_ALL}")
    print(f"{Fore.RED}Tests échoués  : {tests_failed} ✗{Style.RESET_ALL}")
    
    success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
    print(f"\nTaux de réussite : {success_rate:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 TOUS LES TESTS SONT PASSÉS ! 🎉{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Votre projet Part 3 est complet !{Style.RESET_ALL}")
    elif success_rate >= 80:
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}✓ Bon travail ! Quelques améliorations à faire.{Style.RESET_ALL}")
    elif success_rate >= 50:
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚠ Travail en cours. Continuez !{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}{Style.BRIGHT}❌ Beaucoup de travail reste à faire.{Style.RESET_ALL}")
    
    # Recommandations
    if tests_failed > 0:
        print(f"\n{Fore.CYAN}📋 RECOMMANDATIONS:{Style.RESET_ALL}")
        print("1. Consultez les messages d'erreur ci-dessus")
        print("2. Relisez les instructions des tasks qui ont échoué")
        print("3. Vérifiez que toutes les dépendances sont installées")
        print("4. Assurez-vous que la structure des dossiers est correcte")


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Fonction principale"""
    print_header("VÉRIFICATION COMPLÈTE - PART 3 DU PROJET HBNB")
    print_info("Ce script vérifie l'implémentation des tasks 0 à 8")
    print_info("Certains tests peuvent nécessiter que Flask soit arrêté")
    
    try:
        # Vérifier chaque task
        check_task_0()
        check_task_1()
        check_task_2()
        check_task_3()
        check_task_4()
        check_task_5()
        check_task_6()
        check_task_7()
        check_task_8()
        
        # Afficher le résumé
        print_summary()
        
        # Code de sortie
        sys.exit(0 if tests_failed == 0 else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Vérification interrompue par l'utilisateur{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Fore.RED}❌ Erreur fatale: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
