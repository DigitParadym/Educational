#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement de l'interface depuis n'importe quel dossier
"""

import sys
import os
from pathlib import Path

def lancer_interface():
    """Lance l'interface GUI depuis le bon dossier."""
    
    # Trouver le dossier de l'interface
    dossier_courant = Path(__file__).parent
    dossier_interface = dossier_courant / "composants_browser"
    
    if not dossier_interface.exists():
        print("ERREUR: Dossier composants_browser non trouve")
        print(f"Cherche dans: {dossier_interface}")
        return False
    
    fichier_interface = dossier_interface / "interface_gui_principale.py"
    
    if not fichier_interface.exists():
        print("ERREUR: interface_gui_principale.py non trouve")
        print(f"Cherche: {fichier_interface}")
        return False
    
    # Changer vers le dossier de l'interface
    os.chdir(dossier_interface)
    print(f"Lancement depuis: {dossier_interface}")
    
    # Lancer l'interface
    try:
        import subprocess
        subprocess.run([sys.executable, "interface_gui_principale.py"])
        return True
    except Exception as e:
        print(f"ERREUR lancement: {e}")
        return False

if __name__ == "__main__":
    print("LANCEMENT INTERFACE AST")
    print("=" * 30)
    lancer_interface()
