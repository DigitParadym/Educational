#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur Principal des Tests AST - Version Amelioree
==================================================

Ce script lance tous les types de tests du systeme AST :
- Tests d'imports
- Tests systeme core
- Tests interface GUI  
- Tests unitaires complets
- Copie automatique des resultats vers le presse-papiers

Usage:
    python tests/run_tests.py
"""

import sys
import os
import subprocess
import unittest
from pathlib import Path
from io import StringIO
import contextlib

def copy_to_clipboard(text):
    """Copie le texte vers le presse-papiers."""
    try:
        # Windows
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text, text=True, check=True)
            return True
        # macOS
        elif sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        # Linux
        else:
            # Essayer xclip puis xsel
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], 
                             input=text, text=True, check=True)
                return True
            except:
                subprocess.run(["xsel", "--clipboard", "--input"], 
                             input=text, text=True, check=True)
                return True
    except Exception as e:
        print(f"Erreur copie presse-papiers: {e}")
        return False

def tester_imports():
    """Teste les imports essentiels."""
    print("=== TEST IMPORTS ===")
    
    # Ajouter le chemin racine
    root_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(root_dir))
    
    try:
        import modificateur_interactif
        print("+ modificateur_interactif: OK")
        return True
    except ImportError as e:
        print(f"X modificateur_interactif: {e}")
        return False

def tester_systeme_core():
    """Teste le systeme core."""
    print("\n=== TEST SYSTEME CORE ===")
    
    try:
        from core.transformation_loader import TransformationLoader
        loader = TransformationLoader()
        transformations = loader.list_transformations()
        
        print(f"+ Transformations detectees: {len(transformations)}")
        for name in transformations:
            transformer = loader.get_transformation(name)
            if transformer:
                metadata = transformer.get_metadata()
                print(f"  - {metadata['name']} v{metadata['version']}")
        
        return len(transformations) > 0
        
    except ImportError as e:
        print(f"X Systeme core: {e}")
        return False
    except Exception as e:
        print(f"X Erreur: {e}")
        return False

def tester_interface_gui():
    """Teste l'interface GUI."""
    print("\n=== TEST INTERFACE GUI ===")
    
    try:
        from composants_browser.interface_gui_principale import InterfaceAST
        app = InterfaceAST()
        print("+ Interface GUI: Creation OK")
        
        # Fermer proprement
        try:
            app.root.destroy()
        except:
            pass
        
        return True
        
    except ImportError as e:
        print(f"X Interface GUI: {e}")
        return False
    except Exception as e:
        print(f"X Erreur GUI: {e}")
        return False

def executer_tests_unitaires():
    """Execute les tests unitaires (CORRIGE)."""
    print("\n=== TESTS UNITAIRES ===")
    
    # CORRECTION: Bon chemin vers les tests unitaires
    test_dir = Path(__file__).parent / "unittests"
    
    if not test_dir.exists():
        print(f"X Dossier tests unitaires non trouve: {test_dir}")
        return False, "Dossier unittests manquant"
    
    try:
        # Decouvrir et executer les tests unitaires
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Parcourir chaque sous-dossier
        for subdir in ['core', 'gui', 'system', 'transformations', 'utils']:
            subdir_path = test_dir / subdir
            if subdir_path.exists():
                try:
                    sub_suite = loader.discover(str(subdir_path), pattern='test_*.py')
                    suite.addTest(sub_suite)
                except Exception as e:
                    print(f"Erreur chargement {subdir}: {e}")
        
        # Compter les tests
        test_count = suite.countTestCases()
        print(f"Tests unitaires decouverts: {test_count}")
        
        if test_count == 0:
            return False, "Aucun test unitaire trouve"
        
        # Capture de la sortie
        output_buffer = StringIO()
        
        # Executer avec capture
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            runner = unittest.TextTestRunner(stream=output_buffer, verbosity=1)
            result = runner.run(suite)
        
        # Recuperer la sortie
        test_output = output_buffer.getvalue()
        
        # Analyser les resultats
        success_rate = 0
        if result.testsRun > 0:
            success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        
        print(f"Tests executes: {result.testsRun}")
        print(f"Succes: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"Echecs: {len(result.failures)}")
        print(f"Erreurs: {len(result.errors)}")
        print(f"Taux de reussite: {success_rate:.1f}%")
        
        # Creer un rapport pour les tests unitaires
        unittest_report = f"""
TESTS UNITAIRES - RAPPORT DETAILLE:
- Tests executes: {result.testsRun}
- Succes: {result.testsRun - len(result.failures) - len(result.errors)}
- Echecs: {len(result.failures)}
- Erreurs: {len(result.errors)}
- Taux de reussite: {success_rate:.1f}%

SORTIE COMPLETE:
{test_output}
"""
        
        success = len(result.failures) == 0 and len(result.errors) == 0
        return success, unittest_report
        
    except Exception as e:
        error_msg = f"Erreur execution tests unitaires: {e}"
        print(f"X {error_msg}")
        return False, error_msg

def lancer_interface():
    """Lance l'interface graphique."""
    print("\n=== LANCEMENT INTERFACE ===")
    
    root_dir = Path(__file__).parent.parent
    script_interface = root_dir / "lancer_interface.py"
    
    if not script_interface.exists():
        print("X Script lancer_interface.py non trouve")
        return False
    
    try:
        subprocess.run([sys.executable, str(script_interface)])
        return True
    except Exception as e:
        print(f"X Erreur lancement interface: {e}")
        return False

def executer_tous_les_tests():
    """Execute tous les tests et genere un rapport complet."""
    print("\n" + "=" * 60)
    print("EXECUTION COMPLETE DE TOUS LES TESTS")
    print("=" * 60)
    
    # Collecter tous les resultats
    resultats = []
    rapport_complet = []
    
    rapport_complet.append("RAPPORT COMPLET - TOUS LES TESTS AST")
    rapport_complet.append("=" * 50)
    
    # Test 1: Imports
    print("Phase 1/4: Tests d'imports...")
    import_success = tester_imports()
    resultats.append(("Tests Imports", import_success))
    rapport_complet.append(f"1. Tests Imports: {'SUCCES' if import_success else 'ECHEC'}")
    
    # Test 2: Systeme Core
    print("\nPhase 2/4: Tests systeme core...")
    core_success = tester_systeme_core()
    resultats.append(("Systeme Core", core_success))
    rapport_complet.append(f"2. Systeme Core: {'SUCCES' if core_success else 'ECHEC'}")
    
    # Test 3: Interface GUI
    print("\nPhase 3/4: Tests interface GUI...")
    gui_success = tester_interface_gui()
    resultats.append(("Interface GUI", gui_success))
    rapport_complet.append(f"3. Interface GUI: {'SUCCES' if gui_success else 'ECHEC'}")
    
    # Test 4: Tests Unitaires
    print("\nPhase 4/4: Tests unitaires...")
    unittest_success, unittest_detail = executer_tests_unitaires()
    resultats.append(("Tests Unitaires", unittest_success))
    rapport_complet.append(f"4. Tests Unitaires: {'SUCCES' if unittest_success else 'ECHEC'}")
    
    # Rapport final
    rapport_complet.append("\nRESULTATS DETAILLES:")
    rapport_complet.append("-" * 30)
    
    succes_total = 0
    for nom, resultat in resultats:
        status = "SUCCES" if resultat else "ECHEC"
        rapport_complet.append(f"{status:8} - {nom}")
        if resultat:
            succes_total += 1
    
    # Calcul du score global
    score_global = (succes_total / len(resultats)) * 100
    rapport_complet.append(f"\nSCORE GLOBAL: {succes_total}/{len(resultats)} ({score_global:.1f}%)")
    
    # Ajouter details des tests unitaires si disponibles
    if isinstance(unittest_detail, str):
        rapport_complet.append("\n" + unittest_detail)
    
    # Recommandations
    rapport_complet.append("\nRECOMMANDATIONS:")
    if not import_success:
        rapport_complet.append("- Verifier l'installation des dependances")
    if not core_success:
        rapport_complet.append("- Verifier le dossier core/transformations/")
    if not gui_success:
        rapport_complet.append("- Verifier l'installation de tkinter")
    if not unittest_success:
        rapport_complet.append("- Examiner les echecs de tests unitaires ci-dessus")
    
    # Generer le rapport final
    rapport_final = "\n".join(rapport_complet)
    
    # Afficher le resume
    print("\n" + "=" * 60)
    print("RESUME FINAL")
    print("=" * 60)
    print(rapport_final)
    
    # Copier vers le presse-papiers
    clipboard_content = f"""ANALYSE COMPLETE SYSTEME AST - COPIE POUR IA

{rapport_final}

TIMESTAMP: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Ce rapport contient l'analyse complete de tous les tests du systeme AST.
Merci d'analyser et proposer des corrections pour les echecs detectes.
"""
    
    if copy_to_clipboard(clipboard_content):
        print("\n" + "+" * 50)
        print("+ RAPPORT COMPLET COPIE VERS LE PRESSE-PAPIERS !")
        print("+ Vous pouvez le coller dans une IA avec Ctrl+V")
        print("+ Le rapport contient l'analyse complete du systeme")
        print("+ Tous les tests: imports, core, GUI, unitaires")
        print("+" * 50)
    else:
        print("\n" + "-" * 50)
        print("- Impossible de copier vers le presse-papiers")
        print("+ Copiez manuellement le rapport ci-dessus")
        print("-" * 50)
    
    return score_global == 100.0

def menu_principal():
    """Menu principal interactif."""
    
    while True:
        print("\n" + "=" * 50)
        print("SUITE DE TESTS AST - MENU PRINCIPAL")
        print("=" * 50)
        print("1. Tester les imports")
        print("2. Tester le systeme core")
        print("3. Tester l'interface GUI")
        print("4. Executer tests unitaires")
        print("5. Lancer l'interface graphique")
        print("6. Executer TOUS les tests (avec copie auto)")
        print("0. Quitter")
        
        choix = input("\nChoix (0-6): ").strip()
        
        if choix == "0":
            print("Au revoir!")
            break
        elif choix == "1":
            tester_imports()
        elif choix == "2":
            tester_systeme_core()
        elif choix == "3":
            tester_interface_gui()
        elif choix == "4":
            success, detail = executer_tests_unitaires()
            if success:
                print("+ Tous les tests unitaires ont reussi!")
            else:
                print("- Certains tests unitaires ont echoue")
                print("+ Details disponibles dans le rapport")
        elif choix == "5":
            lancer_interface()
        elif choix == "6":
            success = executer_tous_les_tests()
            if success:
                print("\n+ TOUS LES TESTS ONT REUSSI !")
                print("+ Systeme AST entierement fonctionnel")
            else:
                print("\n- CERTAINS TESTS ONT ECHOUE")
                print("+ Rapport d'analyse copie dans le presse-papiers")
                print("+ Collez-le dans une IA pour obtenir des corrections")
        else:
            print("Choix invalide")
        
        if choix != "0":
            input("\nAppuyez sur Entree pour continuer...")

def main():
    """Point d'entree principal."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # Mode automatique - execute tous les tests
        print("MODE AUTOMATIQUE - EXECUTION COMPLETE")
        executer_tous_les_tests()
    else:
        # Mode interactif
        menu_principal()

if __name__ == "__main__":
    main()