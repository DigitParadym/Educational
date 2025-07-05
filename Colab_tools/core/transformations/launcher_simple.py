#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Transformations - Plugins de Transformation AST
======================================================

Ce module contient tous les plugins de transformation disponibles :
- print_to_logging_transform : Conversion print() -> logging.info()
- add_docstrings_transform : Ajout automatique de docstrings
- json_ai_transformer : Transformations basées sur configuration JSON

Tous les plugins héritent de BaseTransformer et sont automatiquement
découverts par le TransformationLoader.

Usage:
    from core.transformation_loader import TransformationLoader
    loader = TransformationLoader()
    plugins = loader.list_transformations()
"""

from core.base_transformer import BaseTransformer

# Métadonnées du module transformations
__version__ = "2.4.0"
__author__ = "Équipe AST"
__description__ = "Collection de plugins de transformation AST"

# Imports des transformations disponibles (optionnel)
try:
    # Tentative d'import des plugins principaux
    from core.print_to_logging_transform import PrintToLoggingTransform
    from core.add_docstrings_transform import AddDocstringsTransform
    from core.json_ai_transformer import JsonAITransformer
    
    # Liste des transformations disponibles
    AVAILABLE_TRANSFORMATIONS = [
        'print_to_logging_transform',
        'add_docstrings_transform', 
        'json_ai_transformer'
    ]
    
    # Exports publics
    __all__ = [
        'PrintToLoggingTransform',
        'AddDocstringsTransform',
        'JsonAITransformer',
        'AVAILABLE_TRANSFORMATIONS'
    ]
    
    print(f"Module transformations: {len(AVAILABLE_TRANSFORMATIONS)} plugin(s) disponible(s)")
    
except ImportError as e:
    # En cas d'erreur d'import, on continue sans crash
    print(f"Avertissement transformations.__init__: {e}")
    AVAILABLE_TRANSFORMATIONS = []
    __all__ = []

# Fonction utilitaire pour lister les transformations
def list_available_transformations():
    """
    Retourne la liste des transformations disponibles dans ce module.
    
    Returns:
        list: Liste des noms de transformations disponibles
    """
    return AVAILABLE_TRANSFORMATIONS.copy()

# Fonction pour obtenir des informations sur une transformation
def get_transformation_info(name):
    """
    Retourne des informations sur une transformation spécifique.
    
    Args:
        name (str): Nom de la transformation
        
    Returns:
        dict: Informations sur la transformation ou None si non trouvée
    """
    transformations_map = {
        'print_to_logging_transform': {
            'class': 'PrintToLoggingTransform',
            'description': 'Convertit les appels print() en logging.info()',
            'category': 'logging'
        },
        'add_docstrings_transform': {
            'class': 'AddDocstringsTransform', 
            'description': 'Ajoute automatiquement des docstrings aux fonctions',
            'category': 'documentation'
        },
        'json_ai_transformer': {
            'class': 'JsonAITransformer',
            'description': 'Applique des transformations basées sur configuration JSON',
            'category': 'ai-assisted'
        }
    }
    
    return transformations_map.get(name)

# Ajout des fonctions utilitaires aux exports
__all__.extend(['list_available_transformations', 'get_transformation_info'])

# Message informatif pour les développeurs
def module_info():
    """Affiche les informations du module transformations."""
    print(f"Module transformations v{__version__}")
    print(f"Description: {__description__}")
    print(f"Transformations disponibles: {len(AVAILABLE_TRANSFORMATIONS)}")
    for transform in AVAILABLE_TRANSFORMATIONS:
        info = get_transformation_info(transform)
        if info:
            print(f"  - {transform}: {info['description']}")

# Auto-exécution si le module est importé directement
if __name__ == "__main__":
    module_info()