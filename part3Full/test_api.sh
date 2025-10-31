#!/bin/bash

# Script de test automatisé pour l'API HBnB avec création automatique des utilisateurs
# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://127.0.0.1:5000/api/v1"

# IDs utilisateurs (seront mis à jour après création)
ALICE_ID=""
BOB_ID=""

# Tokens
TOKEN_ALICE=""
TOKEN_BOB=""
TOKEN_JOHN=""

# Variables pour stocker les IDs créés
PLACE_ID=""
REVIEW_ID=""

# Compteurs
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction pour afficher un titre de section
print_section() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Fonction pour extraire une valeur JSON simple
extract_json_value() {
    local json="$1"
    local key="$2"
    # Supprime les espaces et retours à la ligne pour une extraction fiable
    echo "$json" | tr -d '\n' | tr -d ' ' | grep -o "\"$key\":\"[^\"]*\"" | head -1 | sed "s/\"$key\":\"\([^\"]*\)\"/\1/"
}

# Fonction pour extraire l'ID d'un utilisateur par email depuis une liste JSON
extract_user_id_by_email() {
    local json="$1"
    local email="$2"
    # Supprime les espaces et retours à la ligne, puis extrait
    echo "$json" | tr -d '\n' | tr -d ' ' | grep -o "{[^}]*\"email\":\"$email\"[^}]*}" | grep -o "\"id\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
}

# Fonction pour créer un utilisateur
create_user() {
    local first_name="$1"
    local last_name="$2"
    local email="$3"
    local password="$4"
    
    response=$(curl -s -X POST "${BASE_URL}/users/" \
        -H "Content-Type: application/json" \
        -d "{\"first_name\":\"${first_name}\",\"last_name\":\"${last_name}\",\"email\":\"${email}\",\"password\":\"${password}\"}")
    
    user_id=$(extract_json_value "$response" "id")
    echo "$user_id"
}

# Fonction pour se connecter et obtenir un token
get_token() {
    local email="$1"
    local password="$2"
    
    response=$(curl -s -X POST "${BASE_URL}/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${email}\",\"password\":\"${password}\"}")
    
    token=$(extract_json_value "$response" "access_token")
    echo "$token"
}

# Fonction pour tester une requête
test_request() {
    local test_name="$1"
    local expected_code="$2"
    local method="$3"
    local endpoint="$4"
    local data="$5"
    local token="$6"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${YELLOW}Test #${TOTAL_TESTS}: ${test_name}${NC}"
    
    if [ -z "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "${BASE_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Extraire les IDs si nécessaire
        if [[ "$test_name" == *"Alice crée une place"* ]]; then
            PLACE_ID=$(extract_json_value "$body" "id")
            if [ -n "$PLACE_ID" ]; then
                echo -e "  ${CYAN}→ Place ID: $PLACE_ID${NC}"
            fi
        fi
        
        if [[ "$test_name" == *"Bob crée une review"* ]]; then
            REVIEW_ID=$(extract_json_value "$body" "id")
            if [ -n "$REVIEW_ID" ]; then
                echo -e "  ${CYAN}→ Review ID: $REVIEW_ID${NC}"
            fi
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Expected: $expected_code, Got: $http_code)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Afficher la réponse (limitée à 200 caractères pour la lisibilité)
    if [ ${#body} -gt 200 ]; then
        echo -e "Response: ${body:0:200}..."
    else
        echo -e "Response: $body"
    fi
    echo ""
}

# ======================
# CRÉATION DES UTILISATEURS
# ======================

print_section "CRÉATION/VÉRIFICATION DES UTILISATEURS"

echo -e "${CYAN}Tentative de création d'Alice...${NC}"
ALICE_ID=$(create_user "Alice" "Smith" "alice@example.com" "password123")

if [ -n "$ALICE_ID" ]; then
    echo -e "${GREEN}✓ Alice créée - ID: $ALICE_ID${NC}"
else
    echo -e "${YELLOW}⚠ Alice existe déjà ou création échouée${NC}"
fi

echo -e "${CYAN}Tentative de création de Bob...${NC}"
BOB_ID=$(create_user "Bob" "Johnson" "bob@example.com" "password456")

if [ -n "$BOB_ID" ]; then
    echo -e "${GREEN}✓ Bob créé - ID: $BOB_ID${NC}"
else
    echo -e "${YELLOW}⚠ Bob existe déjà ou création échouée${NC}"
fi

# ======================
# RÉCUPÉRATION DES IDs DEPUIS LA LISTE
# ======================

if [ -z "$ALICE_ID" ] || [ -z "$BOB_ID" ]; then
    echo -e "\n${CYAN}Récupération des IDs depuis la liste des utilisateurs...${NC}"
    users_list=$(curl -s -X GET "${BASE_URL}/users/")
    
    if [ -z "$ALICE_ID" ]; then
        ALICE_ID=$(extract_user_id_by_email "$users_list" "alice@example.com")
        if [ -n "$ALICE_ID" ]; then
            echo -e "${GREEN}✓ Alice ID récupéré: $ALICE_ID${NC}"
        else
            echo -e "${RED}✗ Impossible de trouver Alice${NC}"
        fi
    fi
    
    if [ -z "$BOB_ID" ]; then
        BOB_ID=$(extract_user_id_by_email "$users_list" "bob@example.com")
        if [ -n "$BOB_ID" ]; then
            echo -e "${GREEN}✓ Bob ID récupéré: $BOB_ID${NC}"
        else
            echo -e "${RED}✗ Impossible de trouver Bob${NC}"
        fi
    fi
fi

# Vérification finale
if [ -z "$ALICE_ID" ]; then
    echo -e "${RED}✗ Impossible de trouver/créer Alice${NC}"
    echo -e "${YELLOW}Debug: Liste des utilisateurs:${NC}"
    curl -s -X GET "${BASE_URL}/users/"
    exit 1
fi

if [ -z "$BOB_ID" ]; then
    echo -e "${RED}✗ Impossible de trouver/créer Bob${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ IDs récupérés avec succès:${NC}"
echo -e "  Alice: $ALICE_ID"
echo -e "  Bob: $BOB_ID"

# ======================
# RÉGÉNÉRATION DES TOKENS
# ======================

print_section "CONNEXION ET RÉCUPÉRATION DES TOKENS JWT"

echo -e "${CYAN}Connexion d'Alice...${NC}"
TOKEN_ALICE=$(get_token "alice@example.com" "password123")
if [ -n "$TOKEN_ALICE" ]; then
    echo -e "${GREEN}✓ Token Alice obtenu${NC}"
else
    echo -e "${RED}✗ Échec de connexion d'Alice${NC}"
    exit 1
fi

echo -e "${CYAN}Connexion de Bob...${NC}"
TOKEN_BOB=$(get_token "bob@example.com" "password456")
if [ -n "$TOKEN_BOB" ]; then
    echo -e "${GREEN}✓ Token Bob obtenu${NC}"
else
    echo -e "${RED}✗ Échec de connexion de Bob${NC}"
    exit 1
fi

echo -e "${CYAN}Connexion de John...${NC}"
TOKEN_JOHN=$(get_token "john2.doe@example.com" "123456")
if [ -n "$TOKEN_JOHN" ]; then
    echo -e "${GREEN}✓ Token John obtenu${NC}"
else
    echo -e "${YELLOW}⚠ John n'existe pas ou échec de connexion (optionnel)${NC}"
fi

# ======================
# DÉBUT DES TESTS
# ======================

print_section "TESTS USERS"

# Test 1: Lister tous les utilisateurs (PUBLIC)
test_request \
    "Lister tous les utilisateurs (PUBLIC)" \
    "200" \
    "GET" \
    "/users/" \
    "" \
    ""

# Test 2: Obtenir les détails d'Alice (PUBLIC)
test_request \
    "Obtenir les détails d'Alice (PUBLIC)" \
    "200" \
    "GET" \
    "/users/${ALICE_ID}" \
    "" \
    ""

# Test 3: Alice modifie son propre profil (PROTÉGÉ)
test_request \
    "Alice modifie son propre profil" \
    "200" \
    "PUT" \
    "/users/${ALICE_ID}" \
    '{"first_name":"Alice Updated","last_name":"Smith"}' \
    "$TOKEN_ALICE"

# Test 4: Bob essaie de modifier le profil d'Alice (DOIT ÉCHOUER)
test_request \
    "Bob essaie de modifier le profil d'Alice (DOIT ÉCHOUER - 403)" \
    "403" \
    "PUT" \
    "/users/${ALICE_ID}" \
    '{"first_name":"Hacked"}' \
    "$TOKEN_BOB"

# Test 5: Alice essaie de modifier son email (DOIT ÉCHOUER)
test_request \
    "Alice essaie de modifier son email (DOIT ÉCHOUER - 400)" \
    "400" \
    "PUT" \
    "/users/${ALICE_ID}" \
    '{"email":"newemail@example.com"}' \
    "$TOKEN_ALICE"

# Test 6: Alice essaie de modifier son password (DOIT ÉCHOUER)
test_request \
    "Alice essaie de modifier son password (DOIT ÉCHOUER - 400)" \
    "400" \
    "PUT" \
    "/users/${ALICE_ID}" \
    '{"password":"newpassword"}' \
    "$TOKEN_ALICE"

print_section "TESTS PLACES"

# Test 7: Alice crée une place
test_request \
    "Alice crée une place" \
    "201" \
    "POST" \
    "/places/" \
    "{\"title\":\"Beautiful Beach House\",\"description\":\"A lovely house by the sea\",\"price\":150.0,\"latitude\":37.7749,\"longitude\":-122.4194,\"owner_id\":\"${ALICE_ID}\",\"amenities\":[]}" \
    "$TOKEN_ALICE"

# Test 8: Lister toutes les places (PUBLIC)
test_request \
    "Lister toutes les places (PUBLIC)" \
    "200" \
    "GET" \
    "/places/" \
    "" \
    ""

# Test 9: Obtenir les détails de la place (PUBLIC)
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Obtenir les détails de la place (PUBLIC)" \
        "200" \
        "GET" \
        "/places/${PLACE_ID}" \
        "" \
        ""
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 10: Alice modifie sa propre place
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Alice modifie sa propre place" \
        "200" \
        "PUT" \
        "/places/${PLACE_ID}" \
        "{\"title\":\"Updated Beach House\",\"description\":\"Updated description\",\"price\":175.0,\"latitude\":37.7749,\"longitude\":-122.4194,\"amenities\":[]}" \
        "$TOKEN_ALICE"
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 11: Bob essaie de modifier la place d'Alice (DOIT ÉCHOUER)
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Bob essaie de modifier la place d'Alice (DOIT ÉCHOUER - 403)" \
        "403" \
        "PUT" \
        "/places/${PLACE_ID}" \
        "{\"title\":\"Hacked Place\",\"latitude\":37.7749,\"longitude\":-122.4194,\"amenities\":[]}" \
        "$TOKEN_BOB"
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 12: Alice essaie de créer une place pour Bob (DOIT ÉCHOUER)
test_request \
    "Alice essaie de créer une place pour Bob (DOIT ÉCHOUER - 403)" \
    "403" \
    "POST" \
    "/places/" \
    "{\"title\":\"Fake Place\",\"description\":\"Test\",\"price\":100.0,\"latitude\":37.7749,\"longitude\":-122.4194,\"owner_id\":\"${BOB_ID}\",\"amenities\":[]}" \
    "$TOKEN_ALICE"

print_section "TESTS REVIEWS"

# Test 13: Bob crée une review pour la place d'Alice
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Bob crée une review pour la place d'Alice" \
        "201" \
        "POST" \
        "/reviews/" \
        "{\"text\":\"Amazing place! Loved it.\",\"rating\":5,\"user_id\":\"${BOB_ID}\",\"place_id\":\"${PLACE_ID}\"}" \
        "$TOKEN_BOB"
else
    echo -e "${RED}SKIP: PLACE_ID non défini - impossible de créer une review${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 14: Alice essaie de reviewer sa propre place (DOIT ÉCHOUER)
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Alice essaie de reviewer sa propre place (DOIT ÉCHOUER - 400)" \
        "400" \
        "POST" \
        "/reviews/" \
        "{\"text\":\"My place is great!\",\"rating\":5,\"user_id\":\"${ALICE_ID}\",\"place_id\":\"${PLACE_ID}\"}" \
        "$TOKEN_ALICE"
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 15: Bob essaie de reviewer la même place deux fois (DOIT ÉCHOUER)
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Bob essaie de reviewer la même place deux fois (DOIT ÉCHOUER - 400)" \
        "400" \
        "POST" \
        "/reviews/" \
        "{\"text\":\"Another review\",\"rating\":4,\"user_id\":\"${BOB_ID}\",\"place_id\":\"${PLACE_ID}\"}" \
        "$TOKEN_BOB"
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 16: Lister toutes les reviews (PUBLIC)
test_request \
    "Lister toutes les reviews (PUBLIC)" \
    "200" \
    "GET" \
    "/reviews/" \
    "" \
    ""

# Test 17: Obtenir les détails d'une review (PUBLIC)
if [ -n "$REVIEW_ID" ]; then
    test_request \
        "Obtenir les détails d'une review (PUBLIC)" \
        "200" \
        "GET" \
        "/reviews/${REVIEW_ID}" \
        "" \
        ""
else
    echo -e "${RED}SKIP: REVIEW_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 18: Bob modifie sa propre review
if [ -n "$REVIEW_ID" ]; then
    test_request \
        "Bob modifie sa propre review" \
        "200" \
        "PUT" \
        "/reviews/${REVIEW_ID}" \
        '{"text":"Updated review: Still amazing!","rating":5}' \
        "$TOKEN_BOB"
else
    echo -e "${RED}SKIP: REVIEW_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 19: Alice essaie de modifier la review de Bob (DOIT ÉCHOUER)
if [ -n "$REVIEW_ID" ]; then
    test_request \
        "Alice essaie de modifier la review de Bob (DOIT ÉCHOUER - 403)" \
        "403" \
        "PUT" \
        "/reviews/${REVIEW_ID}" \
        '{"text":"Hacked review"}' \
        "$TOKEN_ALICE"
else
    echo -e "${RED}SKIP: REVIEW_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 20: Bob supprime sa review
if [ -n "$REVIEW_ID" ]; then
    test_request \
        "Bob supprime sa review" \
        "200" \
        "DELETE" \
        "/reviews/${REVIEW_ID}" \
        "" \
        "$TOKEN_BOB"
else
    echo -e "${RED}SKIP: REVIEW_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 21: Essayer de récupérer la review supprimée (DOIT ÉCHOUER)
if [ -n "$REVIEW_ID" ]; then
    test_request \
        "Essayer de récupérer la review supprimée (DOIT ÉCHOUER - 404)" \
        "404" \
        "GET" \
        "/reviews/${REVIEW_ID}" \
        "" \
        ""
else
    echo -e "${RED}SKIP: REVIEW_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 22: Lister les reviews d'une place
if [ -n "$PLACE_ID" ]; then
    test_request \
        "Lister les reviews d'une place" \
        "200" \
        "GET" \
        "/places/${PLACE_ID}/reviews/" \
        "" \
        ""
else
    echo -e "${RED}SKIP: PLACE_ID non défini${NC}\n"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# ======================
# RÉSUMÉ DES TESTS
# ======================

print_section "RÉSUMÉ DES TESTS"

echo -e "${BLUE}Total de tests: ${TOTAL_TESTS}${NC}"
echo -e "${GREEN}Tests réussis: ${PASSED_TESTS}${NC}"
echo -e "${RED}Tests échoués: ${FAILED_TESTS}${NC}"

if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "${CYAN}Taux de réussite: ${PASS_RATE}%${NC}"
fi

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 Tous les tests ont réussi !${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ ${FAILED_TESTS} test(s) ont échoué.${NC}\n"
    exit 1
fi