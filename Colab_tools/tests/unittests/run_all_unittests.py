#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lanceur de Tous les Tests Unitaires - Version Amelioree
=======================================================

Ce script decouvre et lance automatiquement tous les tests unitaires
dans le dossier tests/unittests/ et ses sous-dossiers.
NOUVEAU: Copie automatique des resultats vers le presse-papiers pour analyse IA.

Usage:
    python tests/unittests/run_all_tests.py
"""

import unittest
import sys
import os
import subprocess
from pathlib import Path

# Ajouter le chemin du projet au sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

def run_all_unittests():
    """Lance tous les tests unitaires."""
    
    print("=" * 60)
    print("EXECUTION DE TOUS LES TESTS UNITAIRES")
    print("=" * 60)
    
    # Dossier de base des tests unitaires
    test_dir = Path(__file__).parent
    
    # Decouvrir tous les tests (en excluant les modules problematiques)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Parcourir chaque sous-dossier et charger les tests manuellement
    for subdir in ['gui', 'system', 'transformations', 'utils']:
        subdir_path = test_dir / subdir
        if subdir_path.exists():
            try:
                # Charger les tests de ce sous-dossier
                sub_suite = loader.discover(str(subdir_path), pattern='test_*.py')
                suite.addTest(sub_suite)
            except Exception as e:
                print(f"Erreur chargement {subdir}: {e}")
    
    # Compter le nombre de tests
    test_count = suite.countTestCases()
    print(f"Tests decouverts: {test_count}")
    
    if test_count == 0:
        report = "ERREUR: Aucun test trouve !"
        print(report)
        copy_to_clipboard(report)
        return False
    
    # Capture de la sortie pour le rapport
    from io import StringIO
    import contextlib
    
    output_buffer = StringIO()
    
    # Lancer tous les tests avec capture de sortie
    with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
        runner = unittest.TextTestRunner(stream=output_buffer, verbosity=2)
        result = runner.run(suite)
    
    # Recuperer la sortie
    test_output = output_buffer.getvalue()
    
    # Creer le rapport detaille
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("RAPPORT COMPLET - TESTS UNITAIRES")
    report_lines.append("=" * 60)
    report_lines.append(f"Tests executes: {result.testsRun}")
    report_lines.append(f"Succes: {result.testsRun - len(result.failures) - len(result.errors)}")
    report_lines.append(f"Echecs: {len(result.failures)}")
    report_lines.append(f"Erreurs: {len(result.errors)}")
    report_lines.append(f"Ignores: {len(result.skipped)}")
    
    # Calculer le pourcentage de reussite
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        report_lines.append(f"Taux de reussite: {success_rate:.1f}%")
    
    # Problemes detectes
    problems_detected = []
    
    if result.failures:
        report_lines.append(f"\nECHECS DETAILLES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            test_name = str(test).split()[0]
            error_summary = traceback.split('\n')[-2] if '\n' in traceback else traceback
            report_lines.append(f"{i}. {test_name}")
            report_lines.append(f"   Erreur: {error_summary}")
            problems_detected.append(f"ECHEC: {test_name} - {error_summary}")
    
    if result.errors:
        report_lines.append(f"\nERREURS DETAILLEES ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            test_name = str(test).split()[0]
            error_summary = traceback.split('\n')[-2] if '\n' in traceback else traceback
            report_lines.append(f"{i}. {test_name}")
            report_lines.append(f"   Erreur: {error_summary}")
            problems_detected.append(f"ERREUR: {test_name} - {error_summary}")
    
    # Problemes specifiques detectes
    report_lines.append("\nPROBLEMES SPECIFIQUES DETECTES:")
    
    if "core\\transformations non trouve" in test_output:
        problems_detected.append("PROBLEME: Dossier core/transformations manquant")
        report_lines.append("- Dossier core/transformations manquant ou mal configure")
    
    if "fix_mutable_defaults_transform non trouve" in test_output:
        problems_detected.append("PROBLEME: Transformateur fix_mutable_defaults_transform absent")
        report_lines.append("- Transformateur fix_mutable_defaults_transform non trouve")
    
    if "add_docstrings_transform" in test_output and "not found" in test_output:
        problems_detected.append("PROBLEME: Transformateur add_docstrings_transform non charge")
        report_lines.append("- Transformateur add_docstrings_transform non charge correctement")
    
    # Recommandations
    report_lines.append("\nRECOMMANDATIONS DE CORRECTION:")
    
    if "core\\transformations non trouve" in test_output:
        report_lines.append("1. Verifier que le dossier core/transformations/ existe")
        report_lines.append("2. S'assurer qu'il contient les fichiers .py des transformateurs")
        report_lines.append("3. Verifier le fichier __init__.py dans core/transformations/")
    
    if result.failures or result.errors:
        report_lines.append("4. Examiner les erreurs specifiques ci-dessus")
        report_lines.append("5. Corriger les problemes d'imports et de chemins")
    
    # Creer le rapport final
    full_report = "\n".join(report_lines)
    
    # Afficher le rapport
    print(full_report)
    
    # Copier vers le presse-papiers
    clipboard_report = f"""ANALYSE TESTS UNITAIRES - COPIE POUR IA

{full_report}

SORTIE COMPLETE DES TESTS:
{test_output}

RESUME POUR IA:
- {result.testsRun} tests executes
- {len(result.failures)} echecs
- {len(result.errors)} erreurs  
- {len(result.skipped)} ignores
- Taux de reussite: {success_rate:.1f}% si {result.testsRun} > 0 sinon "N/A"

PROBLEMES DETECTES:
{chr(10).join(problems_detected) if problems_detected else "Aucun probleme majeur detecte"}

Merci d'analyser ces resultats et de proposer des corrections specifiques.
"""
    
    if copy_to_clipboard(clipboard_report):
        print("\n" + "+" * 50)
        print("+ RAPPORT COPIE VERS LE PRESSE-PAPIERS !")
        print("+ Vous pouvez maintenant le coller dans une IA pour analyse")
        print("+ Utilisez Ctrl+V pour coller le rapport complet")
        print("+ Le rapport contient l'analyse detaillee et les recommandations")
        print("+" * 50)
    else:
        print("\n" + "-" * 50)
        print("- Impossible de copier vers le presse-papiers")
        print("+ Copiez manuellement le rapport ci-dessus")
        print("- Selectionnez tout le texte et faites Ctrl+C")
        print("-" * 50)
    
    # Retourner True si tous les tests passent
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n+ TOUS LES TESTS ONT REUSSI ! ({result.testsRun} tests)")
        print("+ Rapport de succes copie dans le presse-papiers")
        print("+ Vous pouvez le coller avec Ctrl+V pour documentation")
    else:
        print(f"\n- CERTAINS TESTS ONT ECHOUE")
        print(f"+ Details: {len(result.failures)} echecs, {len(result.errors)} erreurs")
        print("+ Rapport d'analyse complet copie dans le presse-papiers")
        print("+ Collez-le dans une IA avec Ctrl+V pour obtenir des corrections")
    
    return success

def list_available_tests():
    """Liste tous les tests disponibles."""
    
    print("=" * 60)
    print("TESTS UNITAIRES DISPONIBLES")
    print("=" * 60)
    
    test_dir = Path(__file__).parent
    
    # Rechercher tous les fichiers de test
    test_files = []
    for pattern in ['test_*.py', '*_test.py']:
        test_files.extend(test_dir.rglob(pattern))
    
    if not test_files:
        print("Aucun fichier de test trouve")
        return
    
    print(f"Fichiers de test trouves: {len(test_files)}")
    
    for test_file in sorted(test_files):
        rel_path = test_file.relative_to(test_dir)
        print(f"  - {rel_path}")
        
        # Compter les tests dans ce fichier
        try:
            loader = unittest.TestLoader()
            suite = loader.discover(str(test_file.parent), pattern=test_file.name)
            test_count = suite.countTestCases()
            print(f"    ({test_count} tests)")
        except:
            print("    (erreur chargement)")

def run_specific_test_file(test_file):
    """Lance un fichier de test specifique."""
    
    print(f"=" * 60)
    print(f"LANCEMENT DU TEST: {test_file}")
    print("=" * 60)
    
    test_dir = Path(__file__).parent
    test_path = test_dir / test_file
    
    if not test_path.exists():
        print(f"Fichier de test non trouve: {test_path}")
        return False
    
    # Charger et lancer le test specifique
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_path.parent), pattern=test_path.name)
    
    if suite.countTestCases() == 0:
        print("Aucun test trouve dans ce fichier")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Rapport
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nResultat: {'SUCCES' if success else 'ECHEC'}")
    
    return success

def main():
    """Point d'entree principal avec menu."""
    
    if len(sys.argv) > 1:
        # Mode ligne de commande
        if sys.argv[1] == "--list":
            list_available_tests()
        elif sys.argv[1] == "--run":
            if len(sys.argv) > 2:
                run_specific_test_file(sys.argv[2])
            else:
                run_all_unittests()
        else:
            print("Usage:")
            print("  python run_all_tests.py         # Lance tous les tests")
            print("  python run_all_tests.py --list  # Liste les tests")
            print("  python run_all_tests.py --run test_file.py  # Lance un test specifique")
    else:
        # Mode interactif
        while True:
            print("\n" + "=" * 40)
            print("MENU TESTS UNITAIRES")
            print("=" * 40)
            print("1. Lancer tous les tests")
            print("2. Lister les tests disponibles")
            print("3. Lancer un test specifique")
            print("0. Quitter")
            
            choix = input("\nChoix (0-3): ").strip()
            
            if choix == "0":
                print("Au revoir!")
                break
            elif choix == "1":
                success = run_all_unittests()
                if success:
                    print("\n+ Tous les tests ont reussi!")
                    print("+ Rapport detaille copie vers le presse-papiers")
                    print("+ Utilisez Ctrl+V pour le coller dans un document")
                else:
                    print("\n- Certains tests ont echoue.")
                    print("+ Rapport d'analyse copie vers le presse-papiers")
                    print("+ Collez-le dans une IA avec Ctrl+V pour obtenir des corrections")
                    print("+ Le rapport contient les details complets et recommandations")
            elif choix == "2":
                list_available_tests()
            elif choix == "3":
                list_available_tests()
                test_file = input("\nNom du fichier de test: ").strip()
                if test_file:
                    run_specific_test_file(test_file)
            else:
                print("Choix invalide")
            
            if choix != "0":
                input("\nAppuyez sur Entree pour continuer...")

if __name__ == "__main__":
    main()