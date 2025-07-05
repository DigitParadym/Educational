#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin de Transformation : Correction des Arguments par Defaut Modifiables
VERSION CORRIGEE - Fix du bug 'Assign' object has no attribute 'lineno'
"""

import ast
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Ajouter le chemin pour importer BaseTransformer
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from base_transformer import BaseTransformer
from core.base_transformer import BaseTransformer

class FixMutableDefaultsTransform(BaseTransformer):
    """
    Transformateur qui corrige les arguments par defaut modifiables.
    VERSION CORRIGEE avec gestion des attributs lineno manquants.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Correction Arguments Mutables"
        self.description = "Corrige les mutable default arguments (listes, dicts, sets)"
        self.version = "1.1"  # Version corrigée
        self.author = "Systeme AST Modulaire"
        self.functions_processed = 0
        self.arguments_fixed = 0
        
        # Types d'objets modifiables a detecter
        self.mutable_types = {
            ast.List: "[]",      # Liste vide
            ast.Dict: "{}",      # Dictionnaire vide
            ast.Set: "set()",    # Set vide
        }
    
    def get_metadata(self):
        """Retourne les metadonnees de cette transformation."""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author
        }
    
    def can_transform(self, code_source):
        """
        Verifie s'il y a des fonctions avec des arguments par defaut modifiables.
        """
        try:
            tree = ast.parse(code_source)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if self._has_mutable_defaults(node):
                        return True
            
            return False
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    def _has_mutable_defaults(self, func_node):
        """
        Verifie si une fonction a des arguments par defaut modifiables.
        """
        if not func_node.args.defaults:
            return False

        for default in func_node.args.defaults:
            # Verifie les listes [] et dictionnaires {}
            if type(default) in self.mutable_types:
                return True

            # Verifie l'appel de fonction set()
            if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == 'set':
                return True

        return False
    def _analyze_mutable_defaults(self, func_node):
        """Analyse les arguments par defaut modifiables d'une fonction."""
        mutable_args = []
        
        if not func_node.args.defaults:
            return mutable_args
        
        # Calculer l'index de debut des arguments avec valeurs par defaut
        total_args = len(func_node.args.args)
        defaults_start = total_args - len(func_node.args.defaults)
        
        # Analyser chaque argument avec valeur par defaut
        for i, default in enumerate(func_node.args.defaults):
            if type(default) in self.mutable_types:
                arg_index = defaults_start + i
                if arg_index < total_args:
                    arg_name = func_node.args.args[arg_index].arg
                    original_value = self.mutable_types[type(default)]
                    
                    mutable_args.append({
                        'name': arg_name,
                        'index': arg_index,
                        'original_type': type(default).__name__,
                        'original_value': original_value,
                        'default_node': default
                    })
        
        return mutable_args
    
    def _create_none_check_statements(self, mutable_args):
        """
        Cree les statements de verification None pour chaque argument.
        VERSION CORRIGEE avec gestion des attributs lineno.
        """
        check_statements = []
        
        for arg_info in mutable_args:
            arg_name = arg_info['name']
            original_value = arg_info['original_value']
            
            # Creer la condition: if arg_name is None:
            condition = ast.Compare(
                left=ast.Name(id=arg_name, ctx=ast.Load()),
                ops=[ast.Is()],
                comparators=[ast.Constant(value=None)]
            )
            
            # Creer l'assignation: arg_name = []/{}/set()
            if original_value == "[]":
                value_node = ast.List(elts=[], ctx=ast.Load())
            elif original_value == "{}":
                value_node = ast.Dict(keys=[], values=[])
            elif original_value == "set()":
                value_node = ast.Call(
                    func=ast.Name(id='set', ctx=ast.Load()),
                    args=[],
                    keywords=[]
                )
            else:
                # Fallback pour types non reconnus
                value_node = ast.Constant(value=None)
            
            assignment = ast.Assign(
                targets=[ast.Name(id=arg_name, ctx=ast.Store())],
                value=value_node
            )
            
            # FIX: Ajouter les attributs lineno et col_offset manquants
            self._fix_node_attributes(assignment)
            self._fix_node_attributes(condition)
            
            # Creer le statement if complet
            if_statement = ast.If(
                test=condition,
                body=[assignment],
                orelse=[]
            )
            
            # FIX: Ajouter les attributs lineno et col_offset
            self._fix_node_attributes(if_statement)
            
            check_statements.append(if_statement)
        
        return check_statements
    
    def _fix_node_attributes(self, node):
        """
        FIX: Ajoute les attributs lineno et col_offset manquants aux noeuds AST.
        """
        if not hasattr(node, 'lineno'):
            node.lineno = 1
        if not hasattr(node, 'col_offset'):
            node.col_offset = 0
        
        # Fixer recursivement tous les noeuds enfants
        for child in ast.iter_child_nodes(node):
            self._fix_node_attributes(child)
    
    def transform(self, code_source):
        """
        Applique la transformation de correction des arguments modifiables.
        VERSION CORRIGEE avec gestion des erreurs AST.
        """
        try:
            # Reset des compteurs
            self.functions_processed = 0
            self.arguments_fixed = 0
            
            tree = ast.parse(code_source)
            
            # Transformer l'arbre AST
            transformer = MutableDefaultsNodeTransformer(self)
            modified_tree = transformer.visit(tree)
            
            # FIX: Fixer les attributs sur l'arbre complet
            ast.fix_missing_locations(modified_tree)
            
            # Reconvertir en code
            modified_code = ast.unparse(modified_tree)
            
            print(f"+ Fonctions analysees: {self.functions_processed}")
            print(f"+ Arguments corriges: {self.arguments_fixed}")
            
            return modified_code
            
        except Exception as e:
            print(f"X Erreur transformation mutable defaults: {e}")
            # En cas d'erreur, retourner le code original
            return code_source
    
    def preview_changes(self, code_source):
        """Previsualise les changements sans les appliquer."""
        try:
            tree = ast.parse(code_source)
            functions_with_issues = []
            total_functions = 0
            total_mutable_args = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    total_functions += 1
                    mutable_args = self._analyze_mutable_defaults(node)
                    
                    if mutable_args:
                        total_mutable_args += len(mutable_args)
                        
                        # Determiner le contexte (classe ou module)
                        context = "module"
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.ClassDef):
                                for child in ast.walk(parent):
                                    if child is node:
                                        context = f"classe {parent.name}"
                                        break
                        
                        functions_with_issues.append({
                            'name': node.name,
                            'line': node.lineno,
                            'context': context,
                            'mutable_args': [arg['name'] for arg in mutable_args],
                            'arg_types': [arg['original_type'] for arg in mutable_args]
                        })
            
            return {
                'applicable': len(functions_with_issues) > 0,
                'description': f"Corrigera {total_mutable_args} argument(s) modifiable(s) dans {len(functions_with_issues)} fonction(s)",
                'estimated_changes': total_mutable_args,
                'details': {
                    'total_functions': total_functions,
                    'functions_with_issues': len(functions_with_issues),
                    'total_mutable_arguments': total_mutable_args,
                    'functions_list': functions_with_issues
                }
            }
            
        except Exception as e:
            return {
                'applicable': False,
                'description': f"Erreur d'analyse: {e}",
                'estimated_changes': 0
            }


class MutableDefaultsNodeTransformer(ast.NodeTransformer):
    """
    Visiteur AST qui corrige les arguments par defaut modifiables.
    VERSION CORRIGEE avec gestion des attributs AST.
    """
    
    def __init__(self, parent_transformer):
        self.parent = parent_transformer
    
    def visit_FunctionDef(self, node):
        """Visite les definitions de fonctions."""
        return self._process_function(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Visite les definitions de fonctions async."""
        return self._process_function(node)
    
    def _process_function(self, node):
        """
        Traite une fonction et corrige les arguments modifiables.
        VERSION CORRIGEE avec gestion des attributs AST.
        """
        self.parent.functions_processed += 1
        
        # Analyser les arguments modifiables
        mutable_args = self.parent._analyze_mutable_defaults(node)
        
        if mutable_args:
            print(f"  + Fonction detectee: {node.name}() ligne {node.lineno}")
            
            # Etape 1: Modifier la signature pour remplacer par None
            for arg_info in mutable_args:
                arg_index = arg_info['index']
                default_index = arg_index - (len(node.args.args) - len(node.args.defaults))
                
                # Remplacer la valeur par defaut par None
                none_node = ast.Constant(value=None)
                # FIX: Ajouter les attributs requis
                self.parent._fix_node_attributes(none_node)
                node.args.defaults[default_index] = none_node
                
                print(f"    - Argument '{arg_info['name']}': {arg_info['original_value']} -> None")
                self.parent.arguments_fixed += 1
            
            # Etape 2: Ajouter les verifications None au debut du corps
            check_statements = self.parent._create_none_check_statements(mutable_args)
            
            # Determiner ou inserer les verifications
            insert_position = 0
            
            # Si la fonction a un docstring, l'inserer apres
            if (node.body and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                insert_position = 1
            
            # Inserer les verifications
            for i, check_stmt in enumerate(check_statements):
                node.body.insert(insert_position + i, check_stmt)
            
            print(f"    + {len(check_statements)} verification(s) None ajoutee(s)")
        
        # Continuer la transformation sur les enfants
        self.generic_visit(node)
        return node



    def visit_Call(self, node):
        """Visite les appels de fonction pour transformer set() en None."""
        # Detecter set() vide comme argument par defaut
        if (isinstance(node.func, ast.Name) and 
            node.func.id == 'set' and 
            len(node.args) == 0 and
            len(node.keywords) == 0):
            # Remplacer set() par None
            return ast.Constant(value=None)
        
        return self.generic_visit(node)
# Test rapide si execute directement
if __name__ == "__main__":
    # Test simple
    test_code = '''
def test_function(items=[], options={}):
    """Test function."""
    return items, options
'''
    
    transformer = FixMutableDefaultsTransform()
    print("=== TEST RAPIDE ===")
    print("Code original:")
    print(test_code)
    
    print("\nTransformation:")
    result = transformer.transform(test_code)
    
    print("\nCode transforme:")
    print(result)
