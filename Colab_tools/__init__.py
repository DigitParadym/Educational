#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet AST - Refonte de Code Python
===================================

Système complet de transformation et refactorisation de code Python utilisant
l'arbre syntaxique abstrait (AST) avec une architecture modulaire.

Modules principaux:
- core/ : Système de transformations modulaires
- composants_browser/ : Interface graphique utilisateur
- tests/ : Suite de tests et utilitaires
- test_interface/ : Données de test et exemples

Points d'entrée:
- lancer_interface.py : Interface graphique
- modificateur_interactif.py : Mode interactif
- tests/quick_test_ast_V1.py : Tests rapides
"""

# Métadonnées du projet
__project__ = "Colab AST Tools"
__version__ = "2.4.0"
__author__ = "Équipe AST"
__description__ = "Outils de refactorisation Python par AST"
__license__ = "MIT"

# Configuration du projet
import sys
import os
from pathlib import Path

# Ajouter le répertoire du projet au path Python
_project_root = Path(__file__).parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Imports principaux du projet (optionnels)
try:
    # Importer les modules principaux si disponibles
    from core.transformation_loader import TransformationLoader
    from modificateur_interactif import OrchestrateurAST
    
    # Fonction utilitaire pour accès rapide
    def get_orchestrator():
        """Retourne une instance de l'orchestrateur AST."""
        return OrchestrateurAST()
    
    def get_loader():
        """Retourne une instance du chargeur de transformations."""
        return TransformationLoader()
    
    def list_transformations():
        """Liste toutes les transformations disponibles."""
        loader = get_loader()
        return loader.list_transformations()
    
    # Exports publics
    __all__ = [
        'OrchestrateurAST',
        'TransformationLoader',
        'get_orchestrator',
        'get_loader',
        'list_transformations'
    ]
    
except ImportError as e:
    # En cas d'erreur, on continue sans crash
    print(f"Avertissement __init__: Certains modules ne sont pas disponibles ({e})")
    __all__ = []

# Informations pour les développeurs
def project_info():
    """Affiche les informations du projet."""
    print(f"{__project__} v{__version__}")
    print(f"Description: {__description__}")
    print(f"Auteur: {__author__}")
    print(f"Répertoire: {_project_root}")
    print(f"Modules disponibles: {', '.join(__all__)}")

# Message de bienvenue (optionnel, seulement si importé directement)
if __name__ == "__main__":
    project_info()