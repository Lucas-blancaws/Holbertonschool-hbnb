from app.models.user import User

# 1. Créer un utilisateur
user = User("Alice", "Dupont", "alice@test.com", "secret123")

# 2. Afficher le hash stocké
print("Hash stocké :", user.password)

# 3. Vérifier le mot de passe correct
print("Mot de passe correct ?", user.verify_password("secret123"))

# 4. Vérifier un mot de passe incorrect
print("Mot de passe incorrect ?", user.verify_password("mauvaismdp"))

# 5. Vérifier la sortie de to_dict()
print("to_dict() :", user.to_dict())
