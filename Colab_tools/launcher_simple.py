#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lanceur simple pour l'outil AST - Compatible Windows
Version complete avec detection d'environnement
"""

import sys
import os

# Detection d'environnement
COLAB_ENV = False
VSCODE_ENV = False

try:
    import google.colab
    from google.colab import files
    COLAB_ENV = True
    print("*** Environnement Google Colab detecte ***")
except ImportError:
    pass

try:
    if 'VSCODE_PID' in os.environ or 'JUPYTER_SERVER_ROOT' in os.environ:
        VSCODE_ENV = True
        print("*** Environnement VSCode/Jupyter detecte ***")
except:
    pass

if not COLAB_ENV and not VSCODE_ENV:
    print("*** Environnement Terminal detecte ***")

def main():
    """Point d'entree principal."""
    print(">> Lancement de l'interface graphique AST...")
    
    try:
        # Essayer de lancer l'interface GUI
        from composants_browser.interface_gui_principale import InterfaceAST
        print("+ Interface GUI trouvee")
        
        app = InterfaceAST()
        print("+ Interface creee, lancement...")
        success = app.run()
        
        if success:
            print("+ Interface fermee normalement")
        else:
            print("! Interface fermee avec avertissements")
        
    except ImportError as e:
        print(f"X Erreur import GUI: {e}")
        print(">> Fallback vers modificateur_interactif.py...")
        
        # Fallback vers l'interface originale
        try:
            import modificateur_interactif
            modificateur_interactif.main()
        except Exception as e2:
            print(f"X Erreur fallback: {e2}")
            print(">> Utilisation du fallback simple...")
            
            # Fallback final simple
            fallback_simple()
    
    except Exception as e:
        print(f"X Erreur generale: {e}")
        print(">> Diagnostic de l'environnement...")
        diagnostic_environnement()

def fallback_simple():
    """Fallback simple en cas d'echec total."""
    print("=" * 50)
    print("MODE FALLBACK SIMPLE")
    print("=" * 50)
    print("Aucune interface disponible")
    print("")
    print("Solutions possibles:")
    print("1. Verifiez que tkinter est installe")
    print("2. Testez: python -m tkinter")
    print("3. Reinstallez Python avec tkinter")
    print("4. Utilisez l'interface en ligne de commande")
    print("=" * 50)
    
    reponse = input("Voulez-vous tenter un diagnostic? (o/N): ").strip().lower()
    if reponse in ['o', 'oui', 'y', 'yes']:
        diagnostic_environnement()

def diagnostic_environnement():
    """Diagnostic de l'environnement."""
    print("\n" + "=" * 40)
    print("DIAGNOSTIC DE L'ENVIRONNEMENT")
    print("=" * 40)
    
    # Python
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Repertoire actuel: {os.getcwd()}")
    
    # Variables d'environnement
    print(f"COLAB detecte: {'Oui' if COLAB_ENV else 'Non'}")
    print(f"VSCODE detecte: {'Oui' if VSCODE_ENV else 'Non'}")
    
    # Test tkinter
    try:
        import tkinter
        print(f"Tkinter: OK (version {tkinter.TkVersion})")
        
        # Test creation fenetre
        try:
            root = tkinter.Tk()
            root.withdraw()
            root.destroy()
            print("Test fenetre tkinter: OK")
        except Exception as e:
            print(f"Test fenetre tkinter: ECHEC ({e})")
            
    except ImportError as e:
        print(f"Tkinter: ERREUR - {e}")
        print("Solution: Reinstallez Python avec tkinter")
    
    # Test des modules
    modules_requis = [
        'os', 'sys', 'datetime', 'pathlib', 'traceback'
    ]
    
    print("\nModules requis:")
    for module in modules_requis:
        try:
            __import__(module)
            print(f"  {module}: OK")
        except ImportError:
            print(f"  {module}: MANQUANT")
    
    # Fichiers du projet
    print("\nFichiers du projet:")
    fichiers_attendus = [
        'launcher_simple.py',
        'modificateur_interactif.py',
        'composants_browser/interface_gui_principale.py',
        'composants_browser/__init__.py'
    ]
    
    for fichier in fichiers_attendus:
        if os.path.exists(fichier):
            taille = os.path.getsize(fichier)
            print(f"  {fichier}: OK ({taille} bytes)")
        else:
            print(f"  {fichier}: MANQUANT")
    
    print("=" * 40)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArret par l'utilisateur")
    except Exception as e:
        print(f"\nErreur critique: {e}")
        diagnostic_environnement()
        input("\nAppuyez sur Entree pour fermer...")