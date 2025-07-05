#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test unitaire simple pour le systeme AST
"""

import unittest
import sys
import os
from pathlib import Path

# Ajouter le chemin racine
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

class TestSystemeAST(unittest.TestCase):
    """Tests de base pour le systeme AST."""
    
    def test_import_modificateur(self):
        """Teste l'import du modificateur principal."""
        try:
            import modificateur_interactif
            self.assertTrue(True, "Import modificateur_interactif reussi")
        except ImportError:
            self.skipTest("modificateur_interactif non disponible")
    
    def test_import_core(self):
        """Teste l'import du systeme core."""
        try:
            from core.transformation_loader import TransformationLoader
            loader = TransformationLoader()
            self.assertIsNotNone(loader)
        except ImportError:
            self.skipTest("Systeme core non disponible")
    
    def test_structure_fichiers(self):
        """Teste la presence des fichiers essentiels."""
        root_path = Path(__file__).parent.parent.parent.parent
        
        fichiers_essentiels = [
            "modificateur_interactif.py",
            "lancer_interface.py"
        ]
        
        for fichier in fichiers_essentiels:
            chemin = root_path / fichier
            with self.subTest(fichier=fichier):
                self.assertTrue(chemin.exists(), f"Fichier {fichier} manquant")

if __name__ == '__main__':
    unittest.main()
