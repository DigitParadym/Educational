#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin de Transformation : Ajout de Docstrings Automatique
Ajoute des docstrings par défaut aux fonctions qui n'en ont pas
"""

import ast
import sys
import os
from pathlib import Path

# Ajouter le chemin pour importer BaseTransformer
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from base_transformer import BaseTransformer
from core.base_transformer import BaseTransformer

class AddDocstringsTransform(BaseTransformer):
    """
    Transformer qui ajoute des docstrings par défaut aux fonctions
    et méthodes qui n'en ont pas.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Ajout de Docstrings"
        self.description = "Ajoute des docstrings par défaut aux fonctions sans documentation"
        self.version = "1.0"
        self.author = "Système AST Modulaire"
        self.functions_processed = 0
        self.docstrings_added = 0
    
    def get_metadata(self):
        """Retourne les métadonnées de cette transformation."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }
    
    def can_transform(self, code_source):
        """
        Vérifie s'il y a des fonctions sans docstring dans le code.
        
        Args:
            code_source (str): Code source à analyser
            
        Returns:
            bool: True s'il y a des fonctions sans docstring
        """
        try:
            tree = ast.parse(code_source)
            
            # Chercher les fonctions sans docstring
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not self._has_docstring(node):
                        return True
            
            return False
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _has_docstring(self, func_node):
        """
        Vérifie si une fonction a déjà un docstring.
        
        Args:
            func_node: Nœud AST de la fonction
            
        Returns:
            bool: True si la fonction a un docstring
        """
        if not func_node.body:
            return False
        
        first_stmt = func_node.body[0]
        
        # Vérifier si le premier statement est un docstring
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            if isinstance(first_stmt.value.value, str):
                return True
        
        # Compatibilité Python < 3.8 (ast.Str au lieu de ast.Constant)
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
            return True
        
        return False
    
    def _create_docstring_node(self, func_node):
        """
        Crée un nœud AST pour le docstring par défaut.
        
        Args:
            func_node: Nœud AST de la fonction
            
        Returns:
            ast.Expr: Nœud du docstring
        """
        func_name = func_node.name
        
        # Déterminer le type de fonction
        if func_name.startswith('_') and not func_name.startswith('__'):
            func_type = "méthode privée" if func_name != func_name.lower() else "fonction privée"
        elif func_name.startswith('__') and func_name.endswith('__'):
            func_type = "méthode spéciale"
        elif 'self' in [arg.arg for arg in func_node.args.args]:
            func_type = "méthode"
        else:
            func_type = "fonction"
        
        # Générer le docstring approprié
        if func_name == '__init__':
            docstring_text = """Initialise une nouvelle instance.
            
        TODO: Ajouter la description des paramètres et du comportement.
        """
        elif func_name.startswith('test_'):
            docstring_text = f"""Test unitaire pour {func_name[5:]}.
            
        TODO: Décrire ce que teste cette fonction.
        """
        elif func_name in ['__str__', '__repr__']:
            docstring_text = """Retourne une représentation en chaîne de l'objet.
            
        Returns:
            str: Représentation de l'objet
        """
        elif func_name == '__len__':
            docstring_text = """Retourne la longueur de l'objet.
            
        Returns:
            int: Longueur de l'objet
        """
        else:
            # Analyser les arguments pour créer un docstring plus informatif
            args_info = self._analyze_function_args(func_node)
            
            if args_info['has_args']:
                docstring_text = f"""{func_type.capitalize()} {func_name}.
                
        TODO: Ajouter une description détaillée.
        
        Args:
{args_info['args_doc']}
            
        Returns:
            TODO: Décrire la valeur de retour
        """
            else:
                docstring_text = f"""{func_type.capitalize()} {func_name}.
                
        TODO: Ajouter une description détaillée.
        
        Returns:
            TODO: Décrire la valeur de retour
        """
        
        # Créer le nœud AST pour le docstring
        docstring_node = ast.Expr(
            value=ast.Constant(value=docstring_text)
        )
        
        return docstring_node
    
    def _analyze_function_args(self, func_node):
        """
        Analyse les arguments d'une fonction pour générer la documentation.
        
        Args:
            func_node: Nœud AST de la fonction
            
        Returns:
            dict: Informations sur les arguments
        """
        args_doc_lines = []
        has_meaningful_args = False
        
        # Arguments positionnels
        for arg in func_node.args.args:
            if arg.arg != 'self':  # Ignorer 'self'
                args_doc_lines.append(f"            {arg.arg}: TODO - Décrire ce paramètre")
                has_meaningful_args = True
        
        # Arguments avec valeurs par défaut
        defaults_start = len(func_node.args.args) - len(func_node.args.defaults)
        for i, default in enumerate(func_node.args.defaults):
            arg_index = defaults_start + i
            if arg_index < len(func_node.args.args):
                arg_name = func_node.args.args[arg_index].arg
                if arg_name != 'self':
                    # Essayer de déduire le type depuis la valeur par défaut
                    if isinstance(default, ast.Constant):
                        if isinstance(default.value, bool):
                            type_hint = " (bool, optionnel)"
                        elif isinstance(default.value, int):
                            type_hint = " (int, optionnel)"
                        elif isinstance(default.value, str):
                            type_hint = " (str, optionnel)"
                        elif default.value is None:
                            type_hint = " (optionnel)"
                        else:
                            type_hint = " (optionnel)"
                    else:
                        type_hint = " (optionnel)"
                    
                    args_doc_lines.append(f"            {arg_name}{type_hint}: TODO - Décrire ce paramètre")
                    has_meaningful_args = True
        
        # Arguments *args
        if func_node.args.vararg:
            args_doc_lines.append(f"            *{func_node.args.vararg.arg}: Arguments variables")
            has_meaningful_args = True
        
        # Arguments **kwargs
        if func_node.args.kwarg:
            args_doc_lines.append(f"            **{func_node.args.kwarg.arg}: Arguments de mots-clés")
            has_meaningful_args = True
        
        return {
            'has_args': has_meaningful_args,
            'args_doc': '\n'.join(args_doc_lines) if args_doc_lines else "            Aucun paramètre"
        }
    
    def transform(self, code_source):
        """
        Applique la transformation d'ajout de docstrings.
        
        Args:
            code_source (str): Code source original
            
        Returns:
            str: Code source avec docstrings ajoutés
        """
        try:
            # Reset des compteurs
            self.functions_processed = 0
            self.docstrings_added = 0
            
            tree = ast.parse(code_source)
            
            # Transformer l'arbre AST
            transformer = DocstringNodeTransformer(self)
            modified_tree = transformer.visit(tree)
            
            # Reconvertir en code
            modified_code = ast.unparse(modified_tree)
            
            print(f"+ Fonctions analysées: {self.functions_processed}")
            print(f"+ Docstrings ajoutés: {self.docstrings_added}")
            
            return modified_code
            
        except Exception as e:
            print(f"X Erreur transformation docstrings: {e}")
            return code_source
    
    def preview_changes(self, code_source):
        """
        Prévisualise les changements sans les appliquer.
        
        Args:
            code_source (str): Code source à analyser
            
        Returns:
            dict: Informations sur les changements prévus
        """
        try:
            tree = ast.parse(code_source)
            functions_without_docstring = []
            total_functions = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    if not self._has_docstring(node):
                        # Déterminer le contexte (classe ou module)
                        context = "module"
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.ClassDef):
                                for child in ast.walk(parent):
                                    if child is node:
                                        context = f"classe {parent.name}"
                                        break
                        
                        functions_without_docstring.append({
                            'name': node.name,
                            'line': node.lineno,
                            'context': context
                        })
            
            return {
                'applicable': len(functions_without_docstring) > 0,
                'description': f"Ajoutera des docstrings à {len(functions_without_docstring)} fonction(s)",
                'estimated_changes': len(functions_without_docstring),
                'details': {
                    'total_functions': total_functions,
                    'functions_without_docstring': len(functions_without_docstring),
                    'functions_list': functions_without_docstring
                }
            }
            
        except Exception as e:
            return {
                'applicable': False,
                'description': f"Erreur d'analyse: {e}",
                'estimated_changes': 0
            }


class DocstringNodeTransformer(ast.NodeTransformer):
    """Visiteur AST qui ajoute les docstrings manquants."""
    
    def __init__(self, parent_transformer):
        self.parent = parent_transformer
    
    def visit_FunctionDef(self, node):
        """Visite les définitions de fonctions."""
        return self._process_function(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visite les définitions de fonctions async."""
        return self._process_function(node)
    
    def _process_function(self, node):
        """
        Traite une fonction et ajoute un docstring si nécessaire.
        
        Args:
            node: Nœud AST de la fonction
            
        Returns:
            ast.FunctionDef: Nœud modifié
        """
        self.parent.functions_processed += 1
        
        # Vérifier si la fonction a déjà un docstring
        if not self.parent._has_docstring(node):
            # Créer et ajouter le docstring
            docstring_node = self.parent._create_docstring_node(node)
            
            # Insérer le docstring au début du corps de la fonction
            node.body.insert(0, docstring_node)
            self.parent.docstrings_added += 1
            
            print(f"  + Docstring ajouté à: {node.name}() ligne {node.lineno}")
        
        # Continuer la transformation sur les enfants
        self.generic_visit(node)
        return node
