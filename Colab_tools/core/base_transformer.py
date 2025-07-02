#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de Base pour les Transformations Modulaires
Utilise ABC pour garantir l'implementation des methodes essentielles
"""

import ast
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseTransformer(ABC):
    """
    Classe de base abstraite pour tous les plugins de transformation.
    Chaque transformation doit heriter de cette classe et implementer
    les methodes abstraites.
    """
    
    def __init__(self):
        # Valeurs par defaut (peuvent etre surchargees)
        self.name = "Base Transformer"
        self.description = "Interface de base pour transformations"
        self.version = "1.0"
        self.author = "Core System"
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Retourne les metadonnees de la transformation.
        Essentiel pour l'affichage dans l'interface utilisateur.
        
        Returns:
            dict: Dictionnaire avec name, description, version, author
            
        Example:
            return {
                'name': 'Print vers Logging',
                'description': 'Convertit les appels print() en logging.info()',
                'version': '1.0',
                'author': 'Votre Nom'
            }
        """
        pass
    
    @abstractmethod
    def transform(self, code_source: str) -> str:
        """
        Applique la transformation au code source fourni.
        Prend le code en chaine de caracteres et retourne le code modifie.
        
        Args:
            code_source (str): Code source Python original
            
        Returns:
            str: Code source transforme
            
        Raises:
            Exception: En cas d'erreur de transformation
        """
        pass
    
    def can_transform(self, code_source: str) -> bool:
        """
        Verifie si cette transformation peut s'appliquer au code.
        Par defaut, retourne True (peut etre surchargee).
        
        Args:
            code_source (str): Code source Python a analyser
            
        Returns:
            bool: True si la transformation est applicable
        """
        return True
    
    def get_imports_required(self) -> List[str]:
        """
        Retourne une liste des modules a importer si necessaire.
        Par defaut, aucun import n'est requis.
        
        Returns:
            list: Liste des modules a importer
        """
        return []
    
    def get_config_code(self) -> str:
        """
        Retourne le code de configuration a ajouter.
        Par defaut, aucune configuration.
        
        Returns:
            str: Code de configuration
        """
        return ""
    
    def preview_changes(self, code_source: str) -> Dict[str, Any]:
        """
        Previsualise les changements sans les appliquer.
        Methode optionnelle pour l'interface utilisateur.
        
        Args:
            code_source (str): Code source original
            
        Returns:
            dict: Informations sur les changements prevus
        """
        return {
            'applicable': self.can_transform(code_source),
            'description': self.get_metadata()['description'],
            'estimated_changes': 0
        }
