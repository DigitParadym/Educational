#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests pour TransformationLoader
===============================

Tests unitaires pour transformation_loader
Cree automatiquement et corrige
"""

import unittest
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports du module a tester
try:
    from core.transformation_loader import TransformationLoader
    print("Import TransformationLoader: OK")
except ImportError as e:
    print(f"Erreur import TransformationLoader: {e}")
    TransformationLoader = None


class TestTransformationLoader(unittest.TestCase):
    """
    Classe de tests pour transformation_loader
    """
    
    def setUp(self):
        """
        Methode executee avant chaque test.
        Initialise les objets necessaires pour les tests.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        self.loader = TransformationLoader()
    
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
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        # Test que TransformationLoader peut etre instancie
        self.assertIsNotNone(self.loader)
        self.assertIsInstance(self.loader, TransformationLoader)
    
    def test_basic_functionality(self):
        """
        Test la fonctionnalite de base du module.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        # Test des methodes principales
        self.assertTrue(hasattr(self.loader, 'list_transformations'))
        self.assertTrue(hasattr(self.loader, 'get_transformation'))
        self.assertTrue(hasattr(self.loader, 'get_transformation_metadata'))
        
        # Test que les methodes retournent les bons types
        transformations = self.loader.list_transformations()
        self.assertIsInstance(transformations, list)
        
        metadata = self.loader.get_transformation_metadata()
        self.assertIsInstance(metadata, dict)
    
    def test_error_handling(self):
        """
        Test la gestion des erreurs.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        # Test avec une transformation inexistante
        result = self.loader.get_transformation("transformation_inexistante")
        self.assertIsNone(result)
    
    def test_edge_cases(self):
        """
        Test les cas limites.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        # Test avec des noms vides ou invalides
        result = self.loader.get_transformation("")
        self.assertIsNone(result)
        
        result = self.loader.get_transformation(None)
        self.assertIsNone(result)
    
    def test_real_transformations(self):
        """
        Test avec les vraies transformations disponibles.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        transformations = self.loader.list_transformations()
        
        # Si des transformations sont disponibles, les tester
        if transformations:
            for name in transformations:
                transformer = self.loader.get_transformation(name)
                self.assertIsNotNone(transformer)
                
                # Test que le transformer a les methodes requises
                self.assertTrue(hasattr(transformer, 'get_metadata'))
                self.assertTrue(hasattr(transformer, 'transform'))
                
                # Test des metadata
                metadata = transformer.get_metadata()
                self.assertIsInstance(metadata, dict)
                self.assertIn('name', metadata)
                self.assertIn('version', metadata)


class TestTransformationLoaderIntegration(unittest.TestCase):
    """
    Tests d'integration pour transformation_loader
    """
    
    def test_integration_with_other_modules(self):
        """
        Test l'integration avec d'autres modules.
        """
        if TransformationLoader is None:
            self.skipTest("TransformationLoader non disponible")
        
        # Test integration avec BaseTransformer
        try:
            from core.base_transformer import BaseTransformer
            loader = TransformationLoader()
            transformations = loader.list_transformations()
            
            # Verifier que les transformations chargees heritent de BaseTransformer
            for name in transformations:
                transformer = loader.get_transformation(name)
                if transformer:
                    self.assertIsInstance(transformer, BaseTransformer)
        except ImportError:
            self.skipTest("BaseTransformer non disponible")


def suite():
    """
    Cree une suite de tests pour ce module.
    """
    test_suite = unittest.TestSuite()
    
    # Ajouter les tests unitaires
    test_suite.addTest(unittest.makeSuite(TestTransformationLoader))
    
    # Ajouter les tests d'integration
    test_suite.addTest(unittest.makeSuite(TestTransformationLoaderIntegration))
    
    return test_suite


if __name__ == '__main__':
    # Executer les tests si le fichier est lance directement
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
