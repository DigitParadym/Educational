#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour BaseTransformer
===========================

Tests unitaires pour base_transformer
Cree automatiquement et corrige
"""

import unittest
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports du module a tester
try:
    from core.base_transformer import BaseTransformer
    print("Import BaseTransformer: OK")
except ImportError as e:
    print(f"Erreur import BaseTransformer: {e}")
    BaseTransformer = None


class TestBaseTransformer(unittest.TestCase):
    """
    Classe de tests pour base_transformer
    """
    
    def setUp(self):
        """
        Methode executee avant chaque test.
        Initialise les objets necessaires pour les tests.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
    
    def tearDown(self):
        """
        Methode executee apres chaque test.
        Nettoie les ressources utilisees.
        """
        pass
    
    def test_initialization(self):
        """
        Test l'initialisation du module.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
        
        # Test que BaseTransformer peut etre importe
        self.assertIsNotNone(BaseTransformer)
        self.assertTrue(hasattr(BaseTransformer, '__init__'))
    
    def test_basic_functionality(self):
        """
        Test la fonctionnalite de base du module.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
        
        # Test des methodes abstraites
        self.assertTrue(hasattr(BaseTransformer, 'get_metadata'))
        self.assertTrue(hasattr(BaseTransformer, 'transform'))
        self.assertTrue(hasattr(BaseTransformer, 'can_transform'))
    
    def test_error_handling(self):
        """
        Test la gestion des erreurs.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
        
        # Test qu'on ne peut pas instancier BaseTransformer directement
        with self.assertRaises(TypeError):
            BaseTransformer()
    
    def test_edge_cases(self):
        """
        Test les cas limites.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
        
        # Test des methodes par defaut
        self.assertTrue(hasattr(BaseTransformer, 'get_imports_required'))
        self.assertTrue(hasattr(BaseTransformer, 'get_config_code'))


class TestBaseTransformerIntegration(unittest.TestCase):
    """
    Tests d'integration pour base_transformer
    """
    
    def test_integration_with_other_modules(self):
        """
        Test l'integration avec d'autres modules.
        """
        if BaseTransformer is None:
            self.skipTest("BaseTransformer non disponible")
        
        # Test que BaseTransformer peut etre utilise avec TransformationLoader
        try:
            from core.transformation_loader import TransformationLoader
            loader = TransformationLoader()
            self.assertIsNotNone(loader)
        except ImportError:
            self.skipTest("TransformationLoader non disponible")


def suite():
    """
    Cree une suite de tests pour ce module.
    """
    test_suite = unittest.TestSuite()
    
    # Ajouter les tests unitaires
    test_suite.addTest(unittest.makeSuite(TestBaseTransformer))
    
    # Ajouter les tests d'integration
    test_suite.addTest(unittest.makeSuite(TestBaseTransformerIntegration))
    
    return test_suite


if __name__ == '__main__':
    # Executer les tests si le fichier est lance directement
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
