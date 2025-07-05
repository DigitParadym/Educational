#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transformation: Print vers Logging
Convertit les appels print() en logging.info() et ajoute l'import necessaire
"""

import ast
from typing import Dict, Any, List
from base_transformer import BaseTransformer
from core.base_transformer import BaseTransformer

class PrintToLoggingTransform(BaseTransformer):
    """
    Transformer pour convertir les appels print() en logging.info().
    Plugin respectant le contrat BaseTransformer avec ABC.
    """

    def get_metadata(self) -> Dict[str, Any]:
        """Retourne les metadonnees de cette transformation."""
        return {
            'name': 'Print vers Logging',
            'description': 'Convertit les appels print() en logging.info() et ajoute l\'import necessaire.',
            'version': '2.1',
            'author': 'Systeme Core Enhanced'
        }

    def can_transform(self, code_source: str) -> bool:
        """Verifie s'il y a des print() dans le code."""
        try:
            tree = ast.parse(code_source)
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and 
                    isinstance(node.func, ast.Name) and 
                    node.func.id == 'print'):
                    return True
            return False
        except:
            return False

    def get_imports_required(self) -> List[str]:
        """Cette transformation requiert le module 'logging'."""
        return ["logging"]

    def get_config_code(self) -> str:
        """Retourne la configuration logging a ajouter."""
        return """
# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
"""

    def transform(self, code_source: str) -> str:
        """Applique la transformation en utilisant l'AST."""
        try:
            tree = ast.parse(code_source)
            transformer = _PrintVisitor()
            new_tree = transformer.visit(tree)
            
            # Si des modifications ont eu lieu
            if transformer.transformations_effectuees > 0:
                return ast.unparse(new_tree)
            else:
                # Aucune transformation necessaire
                return code_source
                
        except Exception as e:
            # En cas d'erreur de parsing, retourner le code original
            print(f"! Erreur transformation print_to_logging: {e}")
            return code_source

    def preview_changes(self, code_source: str) -> Dict[str, Any]:
        """Previsualise les changements."""
        try:
            tree = ast.parse(code_source)
            print_count = 0
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and 
                    isinstance(node.func, ast.Name) and 
                    node.func.id == 'print'):
                    print_count += 1
            
            return {
                'applicable': print_count > 0,
                'description': f"Conversion de {print_count} appel(s) print() en logging.info()",
                'estimated_changes': print_count,
                'details': {
                    'print_calls_found': print_count,
                    'imports_to_add': self.get_imports_required(),
                    'config_required': bool(self.get_config_code().strip())
                }
            }
        except Exception as e:
            return {
                'applicable': False,
                'description': f"Erreur d'analyse du code: {e}",
                'estimated_changes': 0
            }

# Classe visiteur AST privee pour cette transformation
class _PrintVisitor(ast.NodeTransformer):
    """Visiteur AST pour transformer print() en logging.info()."""
    
    def __init__(self):
        self.transformations_effectuees = 0

    def visit_Call(self, node: ast.Call):
        """Visite les appels de fonction."""
        self.generic_visit(node)
        
        # Si le noeud est un appel a la fonction 'print'
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.transformations_effectuees += 1
            
            # Cree un nouveau noeud pour 'logging.info()'
            new_func = ast.Attribute(
                value=ast.Name(id='logging', ctx=ast.Load()),
                attr='info',
                ctx=ast.Load()
            )
            node.func = new_func
            
        return node
