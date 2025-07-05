#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Specifique pour Fix Mutable Defaults Transformer
=====================================================

Ce test valide le comportement du transformateur fix_mutable_defaults_transform
qui corrige les defauts mutables dans les parametres de fonction.

Usage:
    python tests/unittests/transformations/test_fix_mutable_defaults.py
    
Ou via pytest:
    pytest tests/unittests/transformations/test_fix_mutable_defaults.py -v
"""

import unittest
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet au sys.path
# Le fichier est dans tests/unittests/transformations/, donc remonter de 3 niveaux
current_file = Path(__file__)
project_root = current_file.parent.parent.parent.parent  # 4 niveaux pour sortir de tests/
sys.path.insert(0, str(project_root))

# Debug: afficher le chemin pour verification
print(f"Chemin du projet: {project_root}")
print(f"Chemin actuel: {Path(__file__).parent}")
print(f"Dossier core existe: {(project_root / 'core').exists()}")
print(f"Fichier transformation_loader existe: {(project_root / 'core' / 'transformation_loader.py').exists()}")
print(f"sys.path contient: {str(project_root) in sys.path}")
print("=" * 50)

from core.transformation_loader import TransformationLoader


class TestFixMutableDefaultsTransformer(unittest.TestCase):
    """Tests specifiques pour le transformateur fix_mutable_defaults."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.loader = TransformationLoader()
        self.transformer = self.loader.get_transformation('fix_mutable_defaults_transform')
        
        # Verifier que le transformateur est bien charge
        if not self.transformer:
            self.skipTest("Transformateur fix_mutable_defaults_transform non trouve")
    
    def test_transformer_metadata(self):
        """Test 1: Verifier les metadonnees du transformateur."""
        metadata = self.transformer.get_metadata()
        
        # Verifier les champs obligatoires
        self.assertIn('name', metadata)
        self.assertIn('description', metadata)
        self.assertIn('version', metadata)
        self.assertIn('author', metadata)
        
        # Verifier que le nom est coherent
        self.assertIn('mutable', metadata['name'].lower())
        
        print(f"Transformateur: {metadata['name']} v{metadata['version']}")
    
    def test_detects_mutable_list_default(self):
        """Test 2: Detecter les defauts mutables avec liste."""
        code_with_mutable_list = '''
def process_items(items=[]):
    """Process a list of items."""
    return len(items)
'''
        
        # Verifier que le transformateur detecte le probleme
        can_transform = self.transformer.can_transform(code_with_mutable_list)
        self.assertTrue(can_transform, 
                       "Le transformateur devrait detecter une liste mutable par defaut")
    
    def test_detects_mutable_dict_default(self):
        """Test 3: Detecter les defauts mutables avec dictionnaire."""
        code_with_mutable_dict = '''
def configure_settings(config={}):
    """Configure application settings."""
    return config.get('debug', False)
'''
        
        # Verifier que le transformateur detecte le probleme
        can_transform = self.transformer.can_transform(code_with_mutable_dict)
        self.assertTrue(can_transform, 
                       "Le transformateur devrait detecter un dictionnaire mutable par defaut")
    
    def test_detects_mutable_set_default(self):
        """Test 4: Detecter les defauts mutables avec set."""
        code_with_mutable_set = '''
def unique_items(items=set()):
    """Get unique items from a set."""
    return len(items)
'''
        
        # Verifier que le transformateur detecte le probleme
        can_transform = self.transformer.can_transform(code_with_mutable_set)
        self.assertTrue(can_transform, 
                       "Le transformateur devrait detecter un set mutable par defaut")
    
    def test_ignores_immutable_defaults(self):
        """Test 5: Ignorer les defauts non mutables."""
        code_with_immutable_defaults = '''
def calculate_result(value=0, name="default", flag=True, data=None):
    """Calculate result with immutable defaults."""
    return value * 2 if flag else 0
'''
        
        # Verifier que le transformateur ignore ce code
        can_transform = self.transformer.can_transform(code_with_immutable_defaults)
        self.assertFalse(can_transform, 
                        "Le transformateur ne devrait pas transformer des defauts immutables")
    
    def test_transforms_mutable_list_correctly(self):
        """Test 6: Transformer correctement une liste mutable."""
        original_code = '''
def process_items(items=[]):
    """Process a list of items."""
    items.append("processed")
    return items
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que la transformation a eu lieu
        self.assertNotEqual(original_code, transformed_code, 
                           "Le code devrait etre transforme")
        
        # Verifier que le parametre par defaut n'est plus une liste
        self.assertNotIn('items=[]', transformed_code, 
                        "Le parametre par defaut ne devrait plus etre une liste vide")
        
        # Verifier que None est utilise comme defaut
        self.assertIn('items=None', transformed_code, 
                     "Le parametre par defaut devrait etre None")
        
        # Verifier qu'une verification None est ajoutee
        self.assertIn('if items is None:', transformed_code, 
                     "Une verification None devrait etre ajoutee")
        
        print("Transformation liste mutable reussie")
    
    def test_transforms_mutable_dict_correctly(self):
        """Test 7: Transformer correctement un dictionnaire mutable."""
        original_code = '''
def configure_app(config={}):
    """Configure the application."""
    config['initialized'] = True
    return config
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que la transformation a eu lieu
        self.assertNotEqual(original_code, transformed_code, 
                           "Le code devrait etre transforme")
        
        # Verifier que le parametre par defaut n'est plus un dictionnaire
        self.assertNotIn('config={}', transformed_code, 
                        "Le parametre par defaut ne devrait plus etre un dictionnaire vide")
        
        # Verifier que None est utilise comme defaut
        self.assertIn('config=None', transformed_code, 
                     "Le parametre par defaut devrait etre None")
        
        # Verifier qu'une verification None est ajoutee
        self.assertIn('if config is None:', transformed_code, 
                     "Une verification None devrait etre ajoutee")
        
        print("Transformation dictionnaire mutable reussie")
    
    def test_handles_multiple_mutable_defaults(self):
        """Test 8: Gerer plusieurs defauts mutables dans une fonction."""
        original_code = '''
def complex_function(items=[], config={}, tags=set()):
    """Function with multiple mutable defaults."""
    return len(items) + len(config) + len(tags)
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que tous les defauts mutables sont transformes
        self.assertNotIn('items=[]', transformed_code)
        self.assertNotIn('config={}', transformed_code)
        self.assertNotIn('tags=set()', transformed_code)
        
        # Verifier que tous utilisent None comme defaut
        self.assertIn('items=None', transformed_code)
        self.assertIn('config=None', transformed_code)
        self.assertIn('tags=None', transformed_code)
        
        print("Transformation multiple defauts mutables reussie")
    
    def test_preserves_function_structure(self):
        """Test 9: Preserver la structure de la fonction."""
        original_code = '''
def example_function(name, items=[], debug=False):
    """Example function with mixed parameters."""
    if debug:
        print(f"Processing {name}")
    return items
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que la signature de fonction est preservee
        self.assertIn('def example_function(', transformed_code)
        self.assertIn('name', transformed_code)
        self.assertIn('debug=False', transformed_code)
        
        # Verifier que les commentaires sont preserves
        self.assertIn('"""Example function with mixed parameters."""', transformed_code)
        
        print("Structure de fonction preservee")
    
    def test_handles_complex_defaults(self):
        """Test 10: Gerer les defauts complexes."""
        original_code = '''
def advanced_function(data=[], options={'debug': True}, items=None):
    """Function with complex mutable defaults."""
    return data, options, items
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que les defauts complexes sont transformes
        self.assertNotIn("data=[]", transformed_code)
        self.assertNotIn("options={'debug': True}", transformed_code)
        
        # Verifier que None reste None
        self.assertIn('items=None', transformed_code)
        
        print("Defauts complexes traites correctement")
    
    def test_code_execution_safety(self):
        """Test 11: Verifier que le code transforme est executables."""
        original_code = '''
def test_function(items=[]):
    """Test function."""
    items.append("test")
    return items
'''
        
        # Appliquer la transformation
        transformed_code = self.transformer.transform(original_code)
        
        # Verifier que le code transforme est syntaxiquement correct
        try:
            compile(transformed_code, '<string>', 'exec')
            print("Code transforme syntaxiquement correct")
        except SyntaxError as e:
            self.fail(f"Code transforme syntaxiquement incorrect: {e}")
        
        # Verifier que le code peut s'executer
        try:
            exec_globals = {}
            exec(transformed_code, exec_globals)
            
            # Tester l'execution de la fonction
            test_func = exec_globals.get('test_function')
            if test_func:
                result = test_func()
                self.assertIsInstance(result, list)
                print("Code transforme executable avec succes")
            
        except Exception as e:
            self.fail(f"Erreur execution code transforme: {e}")
    
    def test_edge_cases(self):
        """Test 12: Tester les cas limites."""
        # Code sans defauts mutables
        code_no_mutable = '''
def simple_function():
    return "hello"
'''
        
        can_transform = self.transformer.can_transform(code_no_mutable)
        self.assertFalse(can_transform, 
                        "Ne devrait pas transformer une fonction sans defauts mutables")
        
        # Code avec defauts mutables imbrique
        code_nested = '''
def outer_function(items=[]):
    def inner_function(data={}):
        return data
    return items
'''
        
        can_transform_nested = self.transformer.can_transform(code_nested)
        self.assertTrue(can_transform_nested, 
                       "Devrait detecter les defauts mutables imbriques")
        
        print("Cas limites traites correctement")


def run_specific_test():
    """Fonction utilitaire pour executer le test specifique."""
    print("=" * 60)
    print("TEST SPECIFIQUE - FIX MUTABLE DEFAULTS TRANSFORMER")
    print("=" * 60)
    
    # Creer la suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFixMutableDefaultsTransformer)
    
    # Executer avec un rapport detaille
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("RESUME DU TEST SPECIFIQUE")
    print("=" * 60)
    print(f"Tests executes: {result.testsRun}")
    print(f"Echecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\nECHECS:")
        for test, traceback in result.failures:
            print(f"- {test}")
            print(f"  {traceback}")
    
    if result.errors:
        print("\nERREURS:")
        for test, traceback in result.errors:
            print(f"- {test}")
            print(f"  {traceback}")
    
    # Retourner True si tous les tests passent
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    # Execution directe du script
    success = run_specific_test()
    sys.exit(0 if success else 1)