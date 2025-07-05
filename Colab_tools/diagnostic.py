#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Rapide du Systeme AST - Version Directe
Teste immediatement votre systeme sans structure complexe
"""

import sys
import os
from pathlib import Path

def test_system_ast():
    """Teste directement le systeme AST."""
    
    print("=== TEST RAPIDE SYSTEME AST ===")
    print("Verification des composants...")
    
    # Test 1: Fichiers essentiels
    print("\n1. FICHIERS ESSENTIELS")
    print("-" * 20)
    
    fichiers_requis = [
        "modificateur_interactif.py",
        "lancer_interface.py",
        "core/base_transformer.py",
        "core/transformation_loader.py",
        "composants_browser/interface_gui_principale.py"
    ]
    
    fichiers_presents = 0
    for fichier in fichiers_requis:
        if os.path.exists(fichier):
            print(f"+ {fichier}")
            fichiers_presents += 1
        else:
            print(f"X {fichier}")
    
    print(f"Fichiers presents: {fichiers_presents}/{len(fichiers_requis)}")
    
    # Test 2: Imports
    print("\n2. IMPORTS MODULES")
    print("-" * 18)
    
    try:
        import modificateur_interactif
        print("+ modificateur_interactif: OK")
    except ImportError as e:
        print(f"X modificateur_interactif: {e}")
        return False
    
    # Test 3: Systeme Core
    print("\n3. SYSTEME CORE")
    print("-" * 15)
    
    try:
        from core.transformation_loader import TransformationLoader
        loader = TransformationLoader()
        transformations = loader.list_transformations()
        
        print(f"+ TransformationLoader: OK")
        print(f"+ Plugins detectes: {len(transformations)}")
        
        if transformations:
            for name in transformations:
                transformer = loader.get_transformation(name)
                if transformer:
                    metadata = transformer.get_metadata()
                    print(f"  - {metadata['name']} v{metadata['version']}")
        else:
            print("! Aucun plugin de transformation trouve")
            print("  Verifiez le dossier core/transformations/")
        
    except ImportError as e:
        print(f"X Core system: {e}")
        print("! Dossier core/ manquant ou mal configure")
    except Exception as e:
        print(f"X Erreur core: {e}")
    
    # Test 4: Interface GUI
    print("\n4. INTERFACE GUI")
    print("-" * 15)
    
    try:
        from composants_browser.interface_gui_principale import InterfaceAST
        print("+ Import InterfaceAST: OK")
        
        # Test creation (sans run)
        app = InterfaceAST()
        print("+ Creation instance: OK")
        
        # Test connexion au moteur
        if hasattr(app, 'orchestrateur') and app.orchestrateur:
            print("+ Connexion moteur: OK")
        else:
            print("! Connexion moteur: Non etablie")
        
        # Fermer proprement
        try:
            app.root.destroy()
        except:
            pass
        
    except ImportError as e:
        print(f"X Interface GUI: {e}")
    except Exception as e:
        print(f"X Erreur GUI: {e}")
    
    # Test 5: Test simple transformation
    print("\n5. TEST TRANSFORMATION")
    print("-" * 22)
    
    try:
        from core.transformation_loader import TransformationLoader
        loader = TransformationLoader()
        transformations = loader.list_transformations()
        
        if transformations:
            # Test avec le premier plugin disponible
            plugin_name = transformations[0]
            transformer = loader.get_transformation(plugin_name)
            
            # Code de test simple
            test_code = '''def test_function():
    print("Hello World")
    print("This is a test")
    return True
'''
            
            if transformer.can_transform(test_code):
                print(f"+ Plugin {plugin_name}: Applicable")
                
                # Appliquer la transformation
                result = transformer.transform(test_code)
                if result != test_code:
                    print("+ Transformation: Modifiee")
                else:
                    print("+ Transformation: Aucun changement")
                
            else:
                print(f"! Plugin {plugin_name}: Non applicable")
        else:
            print("X Aucun plugin pour tester")
    
    except Exception as e:
        print(f"X Erreur test transformation: {e}")
    
    print("\n" + "=" * 40)
    print("TEST TERMINE")
    print("=" * 40)
    
    return True

def test_avec_fichier_exemple():
    """Test avec creation d'un fichier d'exemple."""
    
    print("\n=== CREATION ET TEST FICHIER EXEMPLE ===")
    
    # Creer un fichier d'exemple dans tests/
    if not os.path.exists("tests"):
        os.makedirs("tests")
    
    exemple_path = "tests/exemple_test.py"
    exemple_code = '''#!/usr/bin/env python3

class ExempleClasse:
    def __init__(self, nom):
        self.nom = nom
        print(f"Creation de {nom}")
    
    def methode_test(self):
        print("Execution methode test")
        for i in range(3):
            print(f"Iteration {i}")
        print("Methode terminee")

def fonction_principale():
    print("Debut du programme")
    obj = ExempleClasse("test")
    obj.methode_test()
    print("Fin du programme")

if __name__ == "__main__":
    fonction_principale()
'''
    
    # Sauvegarder le fichier
    with open(exemple_path, 'w') as f:
        f.write(exemple_code)
    
    print(f"+ Fichier exemple cree: {exemple_path}")
    
    # Tester les transformations sur ce fichier
    try:
        from core.transformation_loader import TransformationLoader
        loader = TransformationLoader()
        transformations = loader.list_transformations()
        
        print(f"+ Plugins disponibles: {len(transformations)}")
        
        for plugin_name in transformations:
            transformer = loader.get_transformation(plugin_name)
            metadata = transformer.get_metadata()
            
            print(f"\nTest plugin: {metadata['name']}")
            
            if transformer.can_transform(exemple_code):
                print("  + Applicable")
                
                # Appliquer et sauvegarder
                result = transformer.transform(exemple_code)
                output_path = f"tests/exemple_test_{plugin_name}.py"
                
                with open(output_path, 'w') as f:
                    f.write(result)
                
                print(f"  + Resultat sauve: {output_path}")
            else:
                print("  - Non applicable")
    
    except Exception as e:
        print(f"X Erreur test fichier: {e}")

def menu_test_rapide():
    """Menu pour tests rapides."""
    
    while True:
        print("\n" + "=" * 40)
        print("MENU TEST RAPIDE AST")
        print("=" * 40)
        print("1. Test complet du systeme")
        print("2. Test avec fichier exemple")
        print("3. Lancer interface graphique")
        print("4. Lister les plugins disponibles")
        print("0. Quitter")
        
        choix = input("\nChoix (0-4): ").strip()
        
        if choix == "0":
            print("Au revoir!")
            break
        elif choix == "1":
            test_system_ast()
        elif choix == "2":
            test_avec_fichier_exemple()
        elif choix == "3":
            if os.path.exists("lancer_interface.py"):
                print("Lancement interface...")
                os.system("python lancer_interface.py")
            else:
                print("X lancer_interface.py non trouve")
        elif choix == "4":
            try:
                from core.transformation_loader import TransformationLoader
                loader = TransformationLoader()
                transformations = loader.list_transformations()
                
                print(f"\nPlugins detectes: {len(transformations)}")
                for name in transformations:
                    transformer = loader.get_transformation(name)
                    if transformer:
                        metadata = transformer.get_metadata()
                        print(f"- {metadata['name']} v{metadata['version']}")
                        print(f"  {metadata['description']}")
                        print(f"  Auteur: {metadata['author']}")
                        print()
            except Exception as e:
                print(f"Erreur: {e}")
        else:
            print("Choix invalide")
        
        if choix != "0":
            input("\nAppuyez sur Entree pour continuer...")

def main():
    """Point d'entree principal."""
    
    print("TEST RAPIDE SYSTEME AST")
    print("=" * 25)
    print("Ce script teste rapidement votre systeme AST")
    print("sans creer de structure complexe.")
    
    menu_test_rapide()

if __name__ == "__main__":
    main()
