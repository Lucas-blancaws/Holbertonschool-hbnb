#!/usr/bin/env python3
"""
Script pour nettoyer la base de données avant les tests
"""

from app import create_app
from app.extensions import db

def clean_database():
    """Supprime toutes les données de la base"""
    app = create_app()
    
    with app.app_context():
        print("🧹 Nettoyage de la base de données...")
        
        # Supprimer toutes les tables
        db.drop_all()
        print("   ✅ Tables supprimées")
        
        # Recréer toutes les tables
        db.create_all()
        print("   ✅ Tables recréées")
        
        # Recréer l'utilisateur de test
        from app.services.facade_instance import facade
        
        try:
            facade.create_user({
                "first_name": "John",
                "last_name": "Doe",
                "email": "john2.doe@example.com",
                "password": "123456",
                "is_admin": True
            })
            print("   ✅ Utilisateur de test recréé")
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la création de l'utilisateur: {e}")
        
        print("\n✅ Base de données nettoyée et prête pour les tests!")

if __name__ == '__main__':
    clean_database()