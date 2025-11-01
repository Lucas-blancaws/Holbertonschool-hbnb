#!/usr/bin/env python3
"""
code_scan.py
Scanne le projet Python courant pour repérer des erreurs/smells communs :
- erreurs de syntaxe (py_compile)
- usage de pbcrypt (typo)
- occurrences de credentials[...] en dehors d'app/api/v1/auth.py
- prints de password/hash
- create_user avec password déjà hashé (pattern détectable)
- double hashing heuristique (generate_password_hash suivi d'un create_user)
- recherche d'absence de @jwt_required() pour methods POST/PUT/DELETE dans places.py et reviews.py
Usage: python3 code_scan.py
"""
import os
import re
import sys
import py_compile
from pathlib import Path

ROOT = Path('.').resolve()
PYFILES = list(ROOT.rglob('*.py'))

# Patterns to search
patterns = {
    'pbcrypt_typo': re.compile(r'\bpbcrypt\b'),
    'credentials_access': re.compile(r'credentials\s*\['),
    'print_hash': re.compile(r'print\(.{0,40}(password|hash|HASH|Mot de passe|pwd).{0,40}\)', re.I),
    'generate_hash_in_create': re.compile(r'create_user\s*\(\s*{[^}]*["\']password["\']\s*:\s*bcrypt\.generate_password_hash', re.S),
    'create_user_with_password_literal': re.compile(r'create_user\s*\(\s*{[^}]*["\']password["\']\s*:\s*["\']'),
    'bcrypt_generate': re.compile(r'bcrypt\.generate_password_hash\('),
    'verify_password': re.compile(r'\bverify_password\b'),
}

# Helper to check decorators for methods in file
def check_jwt_required_for_methods(filepath, ns_names=None):
    """
    Heuristically check whether methods post/put/delete inside @api.route classes
    are preceded by @jwt_required() decorator.
    Returns list of tuples (lineno, method, has_jwt)
    """
    results = []
    try:
        lines = filepath.read_text(encoding='utf-8').splitlines()
    except Exception:
        return results
    in_class = False
    class_decorator_block = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # track decorator lines
        if stripped.startswith('@'):
            class_decorator_block.append((i+1, stripped))
            continue
        # detect class based Resource (heuristic for @api.route followed by class)
        if re.match(r'class\s+\w+\(Resource\)\s*:', stripped):
            # start of a class - reset decorator block
            in_class = True
            decorator_block_for_next = class_decorator_block[:]
            class_decorator_block = []
            continue
        # detect method defs within class (post/put/delete)
        m = re.match(r'def\s+(post|put|delete)\s*\(', stripped)
        if m and in_class:
            method = m.group(1)
            # check previous 6 lines for @jwt_required
            start = max(0, i-6)
            context = '\n'.join(lines[start:i])
            has_jwt = bool(re.search(r'@jwt_required\s*\(', context))
            results.append((filepath.relative_to(ROOT), i+1, method, has_jwt))
        # leave class on blank line or dedent (very heuristic)
        if stripped == '' and in_class:
            in_class = False
    return results

def main():
    print(f"Scanning repository at: {ROOT}\nFound {len(PYFILES)} python files.\n")
    summary = {'syntax_errors': [], 'issues': []}

    # 1. Syntax check
    print("== Vérification de la syntaxe (py_compile) ==")
    for p in PYFILES:
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e:
            summary['syntax_errors'].append((p, str(e)))
            print(f"[SYNTAX ERROR] {p}: {e}")
    if not summary['syntax_errors']:
        print("Aucune erreur de syntaxe détectée.\n")
    else:
        print()

    # 2. Pattern searches
    print("== Recherche de patterns suspects ==")
    for p in PYFILES:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception as ex:
            print(f"[WARN] Impossible de lire {p}: {ex}")
            continue

        # pbcrypt typo
        if patterns['pbcrypt_typo'].search(text):
            print(f"[TYPO] 'pbcrypt' trouvé dans {p}")
            summary['issues'].append((p, "pbcrypt typo"))

        # credentials[...] usage - flag if outside auth file
        for m in patterns['credentials_access'].finditer(text):
            if 'auth' not in str(p):
                lineno = text[:m.start()].count('\n') + 1
                print(f"[CREDENTIALS USE] credentials[...] trouvé hors d'auth (fichier: {p}, ligne {lineno})")
                summary['issues'].append((p, f"credentials used outside auth at line {lineno}"))

        # prints containing password/hash
        for m in patterns['print_hash'].finditer(text):
            lineno = text[:m.start()].count('\n') + 1
            print(f"[POSSIBLE SECRET PRINT] print(...) contenant 'password/hash' dans {p} à la ligne {lineno}")
            summary['issues'].append((p, f"print of password/hash at line {lineno}"))

        # create_user with bcrypt.generate_password_hash inlined (possible double-hash risk)
        if patterns['generate_hash_in_create'].search(text):
            print(f"[POTENTIAL DOUBLE HASH] create_user reçoit un bcrypt.generate_password_hash(...) dans {p}")
            summary['issues'].append((p, "create_user called with already hashed password"))

        # create_user with password literal (ok) but inspect
        if patterns['create_user_with_password_literal'].search(text):
            print(f"[CREATE_USER PASS LITERAL] create_user called with literal password in {p} (check whether create_user hashes it).")
            summary['issues'].append((p, "create_user called with literal password - confirm create_user hashes it"))

        # general bcrypt.generate_password_hash usage
        if patterns['bcrypt_generate'].search(text):
            # show lines where used
            for m in patterns['bcrypt_generate'].finditer(text):
                lineno = text[:m.start()].count('\n') + 1
                print(f"[BCRYPT HASH] bcrypt.generate_password_hash used in {p} at line {lineno}")

    print()

    # 3. Check places.py and reviews.py for jwt_required on mutate methods
    check_targets = ['app/api/v1/places.py', 'app/api/v1/reviews.py']
    print("== Vérification heuristique de @jwt_required sur POST/PUT/DELETE pour places/reviews ==")
    for rel in check_targets:
        fp = ROOT / rel
        if not fp.exists():
            print(f"[SKIP] {rel} non trouvé.")
            continue
        results = check_jwt_required_for_methods(fp)
        if not results:
            print(f"[OK] Pas de méthodes post/put/delete détectées ou analyse heuristique n'a rien trouvé dans {rel}.")
            continue
        for file, lineno, method, has_jwt in results:
            if not has_jwt:
                print(f"[MISSING JWT] Méthode '{method}' sans @jwt_required() détectée dans {file} à la ligne {lineno}")
                summary['issues'].append((file, f"method {method} without jwt_required at line {lineno}"))
            else:
                print(f"[OK] Méthode '{method}' protégée par @jwt_required() dans {file} à la ligne {lineno}")

    print()

    # 4. Heuristic: find places where credentials printed or sensitive logs exist in auth file (should not)
    auth_file = ROOT / 'app' / 'api' / 'v1' / 'auth.py'
    if auth_file.exists():
        txt = auth_file.read_text(encoding='utf-8')
        if re.search(r'print\(.{0,60}(credentials|password|token).{0,60}\)', txt, re.I):
            print(f"[DEBUG PRINT] auth.py contient des prints de credentials/password/token - supprimez en prod.")
            summary['issues'].append((auth_file, "debug prints in auth"))

    # Final summary
    print("== Résumé ==")
    if not summary['issues'] and not summary['syntax_errors']:
        print("Aucun problème majeur détecté par les heuristiques du scanner.")
    else:
        print(f"Problèmes détectés : {len(summary['issues'])} issues, {len(summary['syntax_errors'])} syntax errors.")
        for it in summary['issues']:
            print(f" - {it[0]} : {it[1]}")
        for se in summary['syntax_errors']:
            print(f" - Syntax error in {se[0]} : {se[1]}")

    print("\nFin du scan. Interprète les résultats, puis inspecte manuellement les fichiers listés.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
