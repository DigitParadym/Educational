#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemple de Transformateur Correct
=================================

Cet exemple montre la structure correcte d'un transformateur.
"""

from core.base_transformer import BaseTransformer

class ExampleTransformer(BaseTransformer):
    """Exemple de transformateur qui herite correctement de BaseTransformer."""
    
    def get_metadata(self):
        """Retourne les metadonnees du transformateur."""
        return {
            'name': 'Exemple Transformateur',
            'description': 'Exemple de transformateur correct',
            'version': '1.0',
            'author': 'Systeme'
        }
    
    def transform(self, code_source: str) -> str:
        """Transforme le code source."""
        # Exemple: ajoute un commentaire
        return f"# Transforme par ExampleTransformer\n{code_source}"
    
    def can_transform(self, code_source: str) -> bool:
        """Verifie si la transformation peut s'appliquer."""
        return len(code_source.strip()) > 0
