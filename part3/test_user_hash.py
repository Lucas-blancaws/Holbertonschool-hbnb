from app.models.user import User

# Création d'un utilisateur
user = User("Alice", "Dupont", "alice@test.com", "secret123")

# Afficher le hash
print("Hash stocké :", user.password)

# Vérifier mot de passe correct
print("Mot de passe correct ?", user.verify_password("secret123"))

# Vérifier mot de passe incorrect
print("Mot de passe incorrect ?", user.verify_password("mauvaismdp"))

# Vérifier to_dict()
print("to_dict() :", user.to_dict())

