#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration des Tests Unitaires
=================================

Configuration centrale pour tous les tests unitaires.
Cree automatiquement le 2025-07-03 19:13:20
"""

import os
from pathlib import Path

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
CORE_DIR = PROJECT_ROOT / "core"
GUI_DIR = PROJECT_ROOT / "composants_browser"

# Configuration des tests
TEST_CONFIG = {
    'verbosity': 2,
    'failfast': False,
    'buffer': True,
    'catch_ctrl_c': True,
}

# Donnees de test
TEST_DATA = {
    'sample_python_code': '''def hello_world():
    print("Hello, World!")
    return True''',
    
    'sample_code_with_docstring': '''def documented_function():
    """This function is already documented."""
    return "documented" ''',
    
    'sample_invalid_code': '''def invalid_function(
    # Code Python invalide
    return "incomplete" ''',
}

# Fichiers temporaires pour les tests
TEMP_FILES_DIR = TESTS_DIR / "temp"
TEMP_FILES_DIR.mkdir(exist_ok=True)

def get_test_data_path(filename):
    """
    Retourne le chemin vers un fichier de donnees de test.
    """
    return TESTS_DIR / "data" / filename

def get_temp_file_path(filename):
    """
    Retourne le chemin vers un fichier temporaire pour les tests.
    """
    return TEMP_FILES_DIR / filename

def cleanup_temp_files():
    """
    Nettoie les fichiers temporaires crees pendant les tests.
    """
    import shutil
    if TEMP_FILES_DIR.exists():
        shutil.rmtree(TEMP_FILES_DIR)
        TEMP_FILES_DIR.mkdir(exist_ok=True)
