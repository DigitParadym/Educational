#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Core - Système de Transformations AST
============================================

Ce module contient le système principal de transformations modulaires :
- TransformationLoader : Chargeur dynamique de plugins
- BaseTransformer : Interface de base pour les transformations
- Plugins de transformation dans le sous-dossier transformations/

Usage:
    from core.transformation_loader import TransformationLoader
    loader = TransformationLoader()
    transformations = loader.list_transformations()
"""

# Version du module core
__version__ = "2.4.0"
__author__ = "Équipe AST"
__description__ = "Système modulaire de transformations AST pour Python"

# Imports principaux disponibles depuis le module core
try:
    from .transformation_loader import TransformationLoader
    from .base_transformer import BaseTransformer
    
    # Exports publics
    __all__ = [
        'TransformationLoader',
        'BaseTransformer'
    ]
    
except ImportError as e:
    # En cas d'erreur d'import, on continue sans crash
    print(f"Avertissement core.__init__: {e}")
    __all__ = []