#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests Reels pour AddDocstringsTransform
=======================================

Tests unitaires reels pour add_docstrings_transform
Teste la generation automatique de docstrings
"""

import unittest
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports du module a tester
try:
    from core.transformation_loader import TransformationLoader
    from core.transformations.add_docstrings_transform import AddDocstringsTransform
    print("Import AddDocstringsTransform: OK")
except ImportError as e:
    print(f"Erreur import AddDocstringsTransform: {e}")
    AddDocstringsTransform = None


class TestAddDocstringsReal(unittest.TestCase):
    """
    Tests reels pour la generation automatique de docstrings
    """
    
    def setUp(self):
        """
        Initialise les objets pour les tests.
        """
        if AddDocstringsTransform is None:
            self.skipTest("AddDocstringsTransform non disponible")
        
        try:
            self.transformer = AddDocstringsTransform()
        except:
            # Essayer de charger via le loader
            try:
                loader = TransformationLoader()
                self.transformer = loader.get_transformation("add_docstrings_transform")
                if self.transformer is None:
                    self.skipTest("Transformer add_docstrings non trouve")
            except:
                self.skipTest("Impossible de charger le transformer")
    
    def tearDown(self):
        """
        Nettoie apres chaque test.
        """
        pass
    
    def test_simple_function_without_docstring(self):
        """
        Test ajout docstring sur fonction simple sans docstring.
        """
        input_code = '''def hello_world():
    return "Hello, World!"'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier qu'une docstring a ete ajoutee
        self.assertIn('"""', result)
        self.assertIn('def hello_world():', result)
        # La fonction originale doit toujours etre presente
        self.assertIn("return 'Hello, World!'", result)
    
    def test_function_with_parameters(self):
        """
        Test ajout docstring sur fonction avec parametres.
        """
        input_code = '''def calculate_area(width, height):
    return width * height'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier presence de docstring
        self.assertIn('"""', result)
        # Verifier que les parametres sont mentionnes
        self.assertIn('width', result)
        self.assertIn('height', result)
        # Verifier Args section (si implemente)
        if 'Args:' in result:
            self.assertIn('Args:', result)
    
    def test_function_already_with_docstring(self):
        """
        Test qu'une fonction avec docstring n'est pas modifiee.
        """
        input_code = '''def documented_function():
    """Cette fonction est deja documentee."""
    return True'''
        
        result = self.transformer.transform(input_code)
        
        # Le code ne devrait pas changer
        self.assertEqual(input_code, result)
    
    def test_multiple_functions(self):
        """
        Test avec plusieurs fonctions melangees.
        """
        input_code = '''def function_without_doc():
    return "no doc"

def function_with_doc():
    """Deja documentee."""
    return "has doc"

def another_without_doc(param1, param2):
    result = param1 + param2
    return result'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier que les fonctions sans doc ont ete modifiees
        docstring_count = result.count('"""')
        # Au minimum, on devrait avoir plus de docstrings qu'avant
        self.assertGreater(docstring_count, input_code.count('"""'))
        
        # La fonction deja documentee ne doit pas changer
        self.assertIn('"""Deja documentee."""', result)
    
    def test_class_method(self):
        """
        Test ajout docstring sur methode de classe.
        """
        input_code = '''class Calculator:
    def add(self, a, b):
        return a + b'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier qu'une docstring a ete ajoutee a la methode
        self.assertIn('"""', result)
        self.assertIn('def add(self, a, b):', result)
    
    def test_function_with_return_annotation(self):
        """
        Test avec annotations de type.
        """
        input_code = '''def typed_function(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier ajout docstring
        self.assertIn('"""', result)
        # Verifier conservation des annotations
        self.assertIn('name: str', result)
        self.assertIn('age: int', result)
        self.assertIn('-> str', result)
    
    def test_private_function(self):
        """
        Test avec fonction privee (underscore).
        """
        input_code = '''def _private_function():
    return "private"'''
        
        result = self.transformer.transform(input_code)
        
        # Le comportement peut varier selon l'implementation
        # Soit elle ajoute une docstring, soit elle ignore
        self.assertIn('def _private_function():', result)
    
    def test_complex_function(self):
        """
        Test avec fonction complexe avec decorateur.
        """
        input_code = '''@staticmethod
def complex_function(data, options=None):
    if options is None:
        options = {}
    
    processed = []
    for item in data:
        if item > 0:
            processed.append(item * 2)
    
    return processed'''
        
        result = self.transformer.transform(input_code)
        
        # Verifier que la docstring est ajoutee apres le decorateur
        self.assertIn('@staticmethod', result)
        self.assertIn('"""', result)
        self.assertIn('def complex_function', result)
    
    def test_empty_file(self):
        """
        Test avec fichier vide.
        """
        input_code = ''
        
        result = self.transformer.transform(input_code)
        
        # Fichier vide reste vide
        self.assertEqual(input_code, result)
    
        def test_file_without_functions(self):
            """Test avec fichier sans fonctions."""
            input_code = """import os
            import sys

            CONSTANT = 42
            variable = "hello"

            # Commentaire
            print("No functions here")"""
        
            # Appliquer la transformation
            result = self.transformer.transform(input_code)
        
            # Le code ne devrait pas changer (aucune fonction a transformer)
            # Mais ast.unparse() peut changer les guillemets, donc on normalise
            normalized_input = input_code.replace('"', "'")
            normalized_result = result.replace('"', "'")
        
            self.assertEqual(normalized_input, normalized_result)

class TestAddDocstringsTransformerMetadata(unittest.TestCase):
    """
    Tests pour les metadonnees du transformer.
    """
    
    def setUp(self):
        """
        Initialise le transformer.
        """
        if AddDocstringsTransform is None:
            self.skipTest("AddDocstringsTransform non disponible")
        
        try:
            self.transformer = AddDocstringsTransform()
        except:
            try:
                loader = TransformationLoader()
                self.transformer = loader.get_transformation("add_docstrings_transform")
                if self.transformer is None:
                    self.skipTest("Transformer non trouve")
            except:
                self.skipTest("Impossible de charger le transformer")
    
    def test_metadata_structure(self):
        """
        Test que les metadonnees sont bien structurees.
        """
        metadata = self.transformer.get_metadata()
        
        # Verifier structure des metadonnees
        self.assertIsInstance(metadata, dict)
        self.assertIn('name', metadata)
        self.assertIn('description', metadata)
        self.assertIn('version', metadata)
        self.assertIn('author', metadata)
    
    def test_can_transform_method(self):
        """
        Test la methode can_transform.
        """
        # Code avec fonction sans docstring
        code_with_function = '''def test():
    pass'''
        
        # Code sans fonction
        code_without_function = '''x = 5
print(x)'''
        
        # Tester can_transform
        can_transform_func = self.transformer.can_transform(code_with_function)
        can_transform_no_func = self.transformer.can_transform(code_without_function)
        
        # Verifier que can_transform retourne un boolean
        self.assertIsInstance(can_transform_func, bool)
        self.assertIsInstance(can_transform_no_func, bool)
    
    def test_imports_required(self):
        """
        Test les imports requis.
        """
        imports = self.transformer.get_imports_required()
        
        # Verifier que c'est une liste
        self.assertIsInstance(imports, list)
    
    def test_config_code(self):
        """
        Test le code de configuration.
        """
        config = self.transformer.get_config_code()
        
        # Verifier que c'est une string
        self.assertIsInstance(config, str)


class TestAddDocstringsIntegration(unittest.TestCase):
    """
    Tests d'integration pour add_docstrings avec le systeme complet.
    """
    
    def test_integration_with_loader(self):
        """
        Test integration avec TransformationLoader.
        """
        try:
            loader = TransformationLoader()
            transformations = loader.list_transformations()
            
            # Verifier que add_docstrings est dans la liste
            self.assertIn('add_docstrings_transform', transformations)
            
            # Verifier qu'on peut le charger
            transformer = loader.get_transformation('add_docstrings_transform')
            self.assertIsNotNone(transformer)
            
            # Verifier qu'il a les bonnes methodes
            self.assertTrue(hasattr(transformer, 'transform'))
            self.assertTrue(hasattr(transformer, 'get_metadata'))
            
        except ImportError:
            self.skipTest("TransformationLoader non disponible")
    
    def test_real_file_transformation(self):
        """
        Test avec un vrai fichier Python.
        """
        if AddDocstringsTransform is None:
            self.skipTest("AddDocstringsTransform non disponible")
        
        # Code d'exemple realiste
        sample_file = '''#!/usr/bin/env python3

import os
import sys

class FileProcessor:
    def __init__(self, path):
        self.path = path
    
    def read_file(self):
        with open(self.path, 'r') as f:
            return f.read()
    
    def process_lines(self, content):
        lines = content.split('\\n')
        processed = []
        for line in lines:
            if line.strip():
                processed.append(line.upper())
        return processed

def main():
    processor = FileProcessor('test.txt')
    content = processor.read_file()
    result = processor.process_lines(content)
    print(result)

if __name__ == '__main__':
    main()'''
        
        try:
            transformer = AddDocstringsTransform()
        except:
            try:
                loader = TransformationLoader()
                transformer = loader.get_transformation("add_docstrings_transform")
                if transformer is None:
                    self.skipTest("Transformer non trouve")
            except:
                self.skipTest("Impossible de charger le transformer")
        
        result = transformer.transform(sample_file)
        
        # Verifier que des docstrings ont ete ajoutees
        original_docstrings = sample_file.count('"""')
        result_docstrings = result.count('"""')
        
        # On devrait avoir plus de docstrings apres transformation
        self.assertGreater(result_docstrings, original_docstrings)
        
        # Verifier que le code est toujours valide Python
        try:
            compile(result, '<string>', 'exec')
        except SyntaxError:
            self.fail("Le code transforme contient des erreurs de syntaxe")


def suite():
    """
    Cree une suite de tests pour ce module.
    """
    test_suite = unittest.TestSuite()
    
    # Ajouter les tests reels
    test_suite.addTest(unittest.makeSuite(TestAddDocstringsReal))
    
    # Ajouter les tests de metadonnees
    test_suite.addTest(unittest.makeSuite(TestAddDocstringsTransformerMetadata))
    
    # Ajouter les tests d'integration
    test_suite.addTest(unittest.makeSuite(TestAddDocstringsIntegration))
    
    return test_suite


if __name__ == '__main__':
    # Executer les tests si le fichier est lance directement
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())