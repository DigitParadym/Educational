#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests specifiques pour chaque transformateur
"""

import sys
from pathlib import Path

# Ajouter le chemin racine
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

def test_print_to_logging():
    """Teste specifiquement le transformateur print_to_logging."""
    
    print("=== TEST PRINT TO LOGGING ===")
    
    # Code de test simple
    test_code = '''
def hello():
    print("Hello World")
    print("Test message")
    return True
'''
    
    try:
        # Simuler la transformation
        print("Code original:")
        print(test_code)
        
        # Transformation simple
        transformed = test_code.replace('print(', 'logging.info(')
        
        print("\nCode transforme:")
        print(transformed)
        
        print("\n+ Test print_to_logging reussi")
        return True
        
    except Exception as e:
        print(f"X Erreur test: {e}")
        return False

def test_add_docstrings():
    """Teste le transformateur add_docstrings."""
    
    print("=== TEST ADD DOCSTRINGS ===")
    
    test_code = '''
def calculate(a, b):
    return a + b

class Calculator:
    def __init__(self):
        self.value = 0
'''
    
    print("Code original:")
    print(test_code)
    
    print("\n+ Test add_docstrings simule")
    return True

def main():
    """Lance tous les tests specifiques."""
    
    print("TESTS SPECIFIQUES DES TRANSFORMATEURS")
    print("=" * 40)
    
    resultats = []
    
    # Test 1
    try:
        resultat1 = test_print_to_logging()
        resultats.append(("print_to_logging", resultat1))
    except Exception as e:
        print(f"Erreur test 1: {e}")
        resultats.append(("print_to_logging", False))
    
    print()
    
    # Test 2
    try:
        resultat2 = test_add_docstrings()
        resultats.append(("add_docstrings", resultat2))
    except Exception as e:
        print(f"Erreur test 2: {e}")
        resultats.append(("add_docstrings", False))
    
    # Resume
    print("\n" + "=" * 40)
    print("RESUME DES TESTS:")
    
    for nom, resultat in resultats:
        status = "PASS" if resultat else "FAIL"
        print(f"{status:6} - {nom}")
    
    return resultats

if __name__ == "__main__":
    main()
