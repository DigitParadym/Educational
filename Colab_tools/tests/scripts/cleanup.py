#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de nettoyage des fichiers de test
"""

import os
import shutil
from pathlib import Path

def nettoyer_outputs():
    """Nettoie les dossiers de sortie."""
    
    tests_dir = Path(__file__).parent.parent
    
    dossiers_a_nettoyer = [
        tests_dir / "output" / "transformations",
        tests_dir / "output" / "reports", 
        tests_dir / "output" / "logs"
    ]
    
    for dossier in dossiers_a_nettoyer:
        if dossier.exists():
            for fichier in dossier.glob("*"):
                if fichier.is_file():
                    fichier.unlink()
                    print(f"Supprime: {fichier.name}")
    
    print("Nettoyage termine!")

if __name__ == "__main__":
    nettoyer_outputs()
