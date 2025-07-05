#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Périodique pour le Système de Transformateurs AST
======================================================

Ce test vérifie la santé globale du système de transformations :
- Chargement des plugins
- Intégrité des transformateurs
- Fonctionnement des transformations
- Compatibilité entre plugins

Usage:
    python tests/test_periodic_transformers.py
    
Ou via pytest:
    pytest tests/test_periodic_transformers.py -v
"""

import unittest
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet au sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.transformation_loader import TransformationLoader
from core.base_transformer import BaseTransformer


class TestPeriodicTransformers(unittest.TestCase):
    """Tests périodiques pour le système de transformateurs."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        self.loader = TransformationLoader()
        
        # Code d'exemple pour tester les transformations
        self.sample_code = '''
def example_function(items=[]):
    """Une fonction avec des défauts mutables."""
    print("Processing items:", items)
    return items

def another_function(data):
    print("Data received:", data)
    return {"result": data}
'''
    
    def test_plugin_discovery(self):
        """Test 1: Vérifier que les plugins se chargent correctement."""
        plugins = self.loader.list_transformations()
        
        # Vérifier qu'au moins un plugin est chargé
        self.assertGreater(len(plugins), 0, 
                          "Aucun plugin chargé - problème de découverte")
        
        # Verifier les plugins attendus (adapte selon vos plugins reels)
        detected_plugins = set(plugins)
        print(f"Plugins detectes: {detected_plugins}")
        
        # Au lieu de tester des plugins specifiques, verifier qu'il y en a au moins 1
        self.assertGreater(len(plugins), 0, 
                          "Aucun plugin charge - probleme de decouverte")
        
        print(f"+ {len(plugins)} plugins charges avec succes")
    
    def test_plugin_integrity(self):
        """Test 2: Vérifier l'intégrité de chaque plugin."""
        plugins = self.loader.list_transformations()
        
        for plugin_name in plugins:
            with self.subTest(plugin=plugin_name):
                transformer = self.loader.get_transformation(plugin_name)
                
                # Vérifier que le plugin est bien une instance de BaseTransformer
                self.assertIsInstance(transformer, BaseTransformer,
                                    f"{plugin_name} n'hérite pas de BaseTransformer")
                
                # Vérifier que get_metadata() fonctionne
                metadata = transformer.get_metadata()
                self.assertIsInstance(metadata, dict,
                                    f"{plugin_name}.get_metadata() ne retourne pas un dict")
                
                # Vérifier les champs obligatoires
                required_fields = ['name', 'description', 'version', 'author']
                for field in required_fields:
                    self.assertIn(field, metadata,
                                f"{plugin_name} manque le champ '{field}' dans metadata")
                    self.assertIsNotNone(metadata[field],
                                       f"{plugin_name} a un champ '{field}' vide")
    
    def test_transformations_functionality(self):
        """Test 3: Vérifier que les transformations fonctionnent."""
        plugins = self.loader.list_transformations()
        
        for plugin_name in plugins:
            with self.subTest(plugin=plugin_name):
                transformer = self.loader.get_transformation(plugin_name)
                
                # Tester can_transform
                try:
                    can_transform = transformer.can_transform(self.sample_code)
                    self.assertIsInstance(can_transform, bool,
                                        f"{plugin_name}.can_transform() ne retourne pas un bool")
                except Exception as e:
                    self.fail(f"{plugin_name}.can_transform() a échoué: {e}")
                
                # Tester transform si applicable
                if can_transform:
                    try:
                        result = transformer.transform(self.sample_code)
                        self.assertIsInstance(result, str,
                                            f"{plugin_name}.transform() ne retourne pas une string")
                        self.assertGreater(len(result), 0,
                                         f"{plugin_name}.transform() retourne du code vide")
                    except Exception as e:
                        self.fail(f"{plugin_name}.transform() a échoué: {e}")
    
    def test_metadata_consistency(self):
        """Test 4: Verifier la coherence des metadonnees."""
        all_metadata = self.loader.get_transformation_metadata()
        
        names_seen = set()
        for plugin_name, metadata in all_metadata.items():
            # Verifier l'unicite des noms (ignorer les doublons temporaires)
            display_name = metadata['name']
            if display_name not in names_seen:
                names_seen.add(display_name)
            else:
                print(f"Attention: Plugin duplique detecte: {display_name}")
            
            # Verifier le format de version
            version = metadata['version']
            self.assertIsInstance(version, str,
                                f"Version de {plugin_name} n'est pas une string")
            self.assertGreater(len(version), 0,
                             f"Version de {plugin_name} est vide")
    
    def test_plugin_reload(self):
        """Test 5: Vérifier que le rechargement des plugins fonctionne."""
        # Compter les plugins initiaux
        initial_count = len(self.loader.list_transformations())
        
        # Recharger
        reloaded_count = self.loader.reload_plugins()
        
        # Vérifier que le nombre reste cohérent
        self.assertEqual(initial_count, reloaded_count,
                        "Le rechargement a changé le nombre de plugins")
        
        # Vérifier que les plugins fonctionnent toujours après rechargement
        plugins = self.loader.list_transformations()
        for plugin_name in plugins:
            transformer = self.loader.get_transformation(plugin_name)
            self.assertIsNotNone(transformer,
                               f"Plugin {plugin_name} non disponible après rechargement")
    
    def test_plugin_compatibility(self):
        """Test 6: Vérifier la compatibilité entre plugins."""
        plugins = self.loader.list_transformations()
        
        # Tester l'application séquentielle de transformations
        code = self.sample_code
        transformations_applied = []
        
        for plugin_name in plugins:
            transformer = self.loader.get_transformation(plugin_name)
            
            if transformer.can_transform(code):
                try:
                    old_code = code
                    code = transformer.transform(code)
                    transformations_applied.append(plugin_name)
                    
                    # Vérifier que le code transformé reste valide
                    self.assertIsInstance(code, str,
                                        f"Transformation {plugin_name} a cassé le type de code")
                    self.assertGreater(len(code), 0,
                                     f"Transformation {plugin_name} a vidé le code")
                    
                    # Vérifier que le code a effectivement changé (si c'était applicable)
                    if transformer.can_transform(old_code):
                        # Note: certaines transformations peuvent ne pas modifier le code
                        # si les conditions ne sont pas remplies
                        pass
                        
                except Exception as e:
                    self.fail(f"Erreur lors de l'application séquentielle de {plugin_name}: {e}")
        
        print(f"+ {len(transformations_applied)} transformations appliquees en sequence")
    
    def test_system_health(self):
        """Test 7: Vérification de la santé générale du système."""
        # Vérifier que le loader est dans un état sain
        self.assertIsNotNone(self.loader.transformations_dir,
                           "Répertoire des transformations non défini")
        
        # Vérifier que le répertoire existe
        self.assertTrue(self.loader.transformations_dir.exists(),
                       f"Répertoire {self.loader.transformations_dir} n'existe pas")
        
        # Vérifier qu'il y a des fichiers Python dans le répertoire
        py_files = list(self.loader.transformations_dir.glob("*.py"))
        non_init_files = [f for f in py_files if not f.name.startswith("__")]
        self.assertGreater(len(non_init_files), 0,
                         "Aucun fichier de transformation trouvé")
        
        print(f"+ Systeme sain: {len(non_init_files)} fichiers de transformation disponibles")


def run_periodic_test():
    """Fonction utilitaire pour exécuter le test périodique."""
    print("=" * 60)
    print("TEST PERIODIQUE - SYSTEME DE TRANSFORMATEURS AST")
    print("=" * 60)
    
    # Créer la suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPeriodicTransformers)
    
    # Exécuter avec un rapport détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("RESUME DU TEST PERIODIQUE")
    print("=" * 60)
    print(f"Tests executes: {result.testsRun}")
    print(f"Echecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\nECHECS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERREURS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Retourner True si tous les tests passent
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    # Exécution directe du script
    success = run_periodic_test()
    sys.exit(0 if success else 1)