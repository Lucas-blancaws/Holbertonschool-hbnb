#!/usr/bin/env python3
import re

# Lire le fichier
with open('scripts.js', 'r') as f:
    content = f.read()

# Remplacer les endpoints sans slash par des endpoints avec slash
replacements = {
    r"fetch\(`\${API_BASE_URL}/auth/login`": r"fetch(`${API_BASE_URL}/auth/login/`",
    r"fetch\(`\${API_BASE_URL}/places`": r"fetch(`${API_BASE_URL}/places/`",
    r"fetch\(`\${API_BASE_URL}/places/\${placeId}`": r"fetch(`${API_BASE_URL}/places/${placeId}/`",
    r"fetch\(`\${API_BASE_URL}/places/\${placeId}/reviews`": r"fetch(`${API_BASE_URL}/places/${placeId}/reviews/`",
}

for old, new in replacements.items():
    content = re.sub(old, new, content)

# Remplacer aussi les références aux champs
content = content.replace('place.name', 'place.title')
content = content.replace('place.price_per_night', 'place.price')

# Écrire le fichier modifié
with open('scripts.js', 'w') as f:
    f.write(content)

print("✅ scripts.js modifié avec succès!")