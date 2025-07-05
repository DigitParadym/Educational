#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur de rapport basique
"""

import json
import time
from pathlib import Path

def generer_rapport():
    """Genere un rapport basique des tests."""
    
    tests_dir = Path(__file__).parent.parent
    output_dir = tests_dir / "output" / "reports"
    
    # Compter les fichiers
    input_files = len(list((tests_dir / "data" / "input").glob("*.py")))
    
    rapport = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fichiers_input": input_files,
        "structure_ok": True,
        "tests_disponibles": [
            "Tests unitaires",
            "Tests integration", 
            "Tests performance"
        ]
    }
    
    # Sauvegarder le rapport
    rapport_file = output_dir / f"rapport_{int(time.time())}.json"
    
    with open(rapport_file, 'w') as f:
        json.dump(rapport, f, indent=2)
    
    print(f"Rapport genere: {rapport_file}")
    print(f"Fichiers d'entree detectes: {input_files}")
    
    return rapport_file

if __name__ == "__main__":
    generer_rapport()
