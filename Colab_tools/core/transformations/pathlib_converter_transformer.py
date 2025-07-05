#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Transformateur PathLib Converter
================================

Ce transformateur modernise le code Python en convertissant l'ancienne 
manipulation de chemins avec os.path vers la nouvelle approche pathlib.

Transformations effectuées:
- os.path.join() → Path() / operator
- os.path.exists() → Path().exists()
- os.path.isfile() → Path().is_file()
- os.path.isdir() → Path().is_dir()
- os.path.basename() → Path().name
- os.path.dirname() → Path().parent
- os.path.abspath() → Path().resolve()
- open(path) → Path(path).open()
- Ajoute l'import pathlib si nécessaire

Auteur: Système de Transformations AST
Version: 1.0
"""

import ast
import re
from typing import Dict, Any, List
from core.base_transformer import BaseTransformer


class PathLibConverterTransform(BaseTransformer):
    """Convertit les appels os.path vers pathlib.Path."""
    
    def __init__(self):
        super().__init__()
        self.needs_pathlib_import = False
        self.path_variables = set()  # Variables identifiées comme chemins
        
    def get_metadata(self) -> Dict[str, Any]:
        """Retourne les métadonnées du transformateur."""
        return {
            'name': 'PathLib Converter',
            'description': 'Convertit os.path vers pathlib.Path pour moderniser le code',
            'version': '1.0',
            'author': 'Système AST'
        }
    
    def can_transform(self, code_source: str) -> bool:
        """Vérifie si le code contient des appels os.path à convertir."""
        os_path_patterns = [
            r'os\.path\.',
            r'from os\.path import',
            r'import os\.path'
        ]
        
        for pattern in os_path_patterns:
            if re.search(pattern, code_source):
                return True
        return False
    
    def transform(self, code_source: str) -> str:
        """Applique la transformation os.path vers pathlib."""
        try:
            # Parser le code en AST
            tree = ast.parse(code_source)
            
            # Analyser et transformer
            transformer = PathLibNodeTransformer()
            new_tree = transformer.visit(tree)
            
            # Reconvertir en code
            import astor
            new_code = astor.to_source(new_tree)
            
            # Ajouter l'import pathlib si nécessaire
            if transformer.needs_pathlib_import:
                new_code = self._add_pathlib_import(new_code)
            
            # Nettoyage final
            new_code = self._cleanup_code(new_code)
            
            return new_code
            
        except Exception as e:
            print(f"Erreur transformation pathlib: {e}")
            return code_source
    
    def _add_pathlib_import(self, code: str) -> str:
        """Ajoute l'import pathlib si nécessaire."""
        lines = code.split('\n')
        
        # Vérifier si pathlib est déjà importé
        has_pathlib = any('from pathlib import Path' in line or 
                         'import pathlib' in line for line in lines)
        
        if has_pathlib:
            return code
        
        # Trouver où insérer l'import
        import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_line = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        # Insérer l'import
        lines.insert(import_line, 'from pathlib import Path')
        
        return '\n'.join(lines)
    
    def _cleanup_code(self, code: str) -> str:
        """Nettoie le code généré."""
        # Supprimer les imports os.path inutiles
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Supprimer import os.path si plus utilisé
            if ('import os.path' in line or 'from os.path import' in line) and 'os.path.' not in code:
                continue
            cleaned_lines.append(line)
        
        # Supprimer les lignes vides en excès
        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        return result


class PathLibNodeTransformer(ast.NodeTransformer):
    """Transformateur AST pour convertir os.path vers pathlib."""
    
    def __init__(self):
        self.needs_pathlib_import = False
        self.path_variables = set()
    
    def visit_Attribute(self, node):
        """Convertit les appels os.path.* vers Path().*"""
        
        # os.path.join(a, b) → Path(a) / b
        if (isinstance(node.value, ast.Attribute) and 
            isinstance(node.value.value, ast.Name) and
            node.value.value.id == 'os' and 
            node.value.attr == 'path'):
            
            self.needs_pathlib_import = True
            
            # Conversion selon la méthode
            if node.attr == 'join':
                return self._convert_join_to_path_operator(node)
            elif node.attr == 'exists':
                return self._convert_to_path_method(node, 'exists')
            elif node.attr == 'isfile':
                return self._convert_to_path_method(node, 'is_file')
            elif node.attr == 'isdir':
                return self._convert_to_path_method(node, 'is_dir')
            elif node.attr == 'basename':
                return self._convert_to_path_property(node, 'name')
            elif node.attr == 'dirname':
                return self._convert_to_path_property(node, 'parent')
            elif node.attr == 'abspath':
                return self._convert_to_path_method(node, 'resolve')
        
        return self.generic_visit(node)
    
    def visit_Call(self, node):
        """Convertit les appels de fonction spéciaux."""
        
        # os.path.join(a, b, c) → Path(a) / b / c
        if (isinstance(node.func, ast.Attribute) and
            isinstance(node.func.value, ast.Attribute) and
            isinstance(node.func.value.value, ast.Name) and
            node.func.value.value.id == 'os' and
            node.func.value.attr == 'path' and
            node.func.attr == 'join'):
            
            self.needs_pathlib_import = True
            return self._create_path_join_chain(node.args)
        
        # open(path, ...) → Path(path).open(...)
        elif (isinstance(node.func, ast.Name) and 
              node.func.id == 'open' and 
              len(node.args) > 0):
            
            # Heuristique simple: si le premier argument ressemble à un chemin
            first_arg = node.args[0]
            if self._looks_like_path(first_arg):
                self.needs_pathlib_import = True
                return self._convert_open_to_path_open(node)
        
        return self.generic_visit(node)
    
    def _convert_to_path_method(self, node, method_name):
        """Convertit vers une méthode Path."""
        # Créer Path(arg).method()
        def create_path_method_call(path_arg):
            path_call = ast.Call(
                func=ast.Name(id='Path', ctx=ast.Load()),
                args=[path_arg],
                keywords=[]
            )
            return ast.Call(
                func=ast.Attribute(value=path_call, attr=method_name, ctx=ast.Load()),
                args=[],
                keywords=[]
            )
        return create_path_method_call
    
    def _convert_to_path_property(self, node, property_name):
        """Convertit vers une propriété Path."""
        def create_path_property(path_arg):
            path_call = ast.Call(
                func=ast.Name(id='Path', ctx=ast.Load()),
                args=[path_arg],
                keywords=[]
            )
            return ast.Attribute(value=path_call, attr=property_name, ctx=ast.Load())
        return create_path_property
    
    def _create_path_join_chain(self, args):
        """Crée une chaîne Path(a) / b / c."""
        if not args:
            return ast.Call(func=ast.Name(id='Path', ctx=ast.Load()), args=[], keywords=[])
        
        # Commencer par Path(premier_arg)
        result = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[args[0]],
            keywords=[]
        )
        
        # Ajouter / arg pour chaque argument suivant
        for arg in args[1:]:
            result = ast.BinOp(
                left=result,
                op=ast.Div(),  # Opérateur /
                right=arg
            )
        
        return result
    
    def _convert_open_to_path_open(self, node):
        """Convertit open(path) vers Path(path).open()."""
        path_arg = node.args[0]
        
        # Créer Path(path_arg)
        path_call = ast.Call(
            func=ast.Name(id='Path', ctx=ast.Load()),
            args=[path_arg],
            keywords=[]
        )
        
        # Créer Path(path_arg).open(autres_args)
        return ast.Call(
            func=ast.Attribute(value=path_call, attr='open', ctx=ast.Load()),
            args=node.args[1:],  # Tous les arguments sauf le premier
            keywords=node.keywords
        )
    
    def _looks_like_path(self, node):
        """Heuristique pour détecter si un argument ressemble à un chemin."""
        # String littérale contenant / ou \
        if isinstance(node, ast.Str):
            return '/' in node.s or '\\' in node.s or '.' in node.s
        
        # Variable avec nom suggérant un chemin
        elif isinstance(node, ast.Name):
            path_keywords = ['path', 'file', 'dir', 'folder', 'chemin', 'fichier']
            return any(keyword in node.id.lower() for keyword in path_keywords)
        
        return False
    
    def get_imports_required(self) -> List[str]:
        """Retourne les imports requis."""
        return ['pathlib'] if self.needs_pathlib_import else []
    
    def preview_changes(self, code_source: str) -> Dict[str, Any]:
        """Prévisualise les changements."""
        os_path_count = len(re.findall(r'os\.path\.', code_source))
        
        return {
            'applicable': self.can_transform(code_source),
            'description': 'Conversion os.path vers pathlib.Path',
            'estimated_changes': os_path_count,
            'impact': 'Modernisation du code, amélioration de la lisibilité'
        }


# Exemple d'utilisation pour les tests
if __name__ == "__main__":
    transformer = PathLibConverterTransform()
    
    # Code d'exemple à transformer
    sample_code = '''
import os

def process_files(base_dir, filename):
    full_path = os.path.join(base_dir, filename)
    
    if os.path.exists(full_path):
        if os.path.isfile(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            
            backup_dir = os.path.dirname(full_path)
            file_name = os.path.basename(full_path)
            
            return content
    return None
'''
    
    print("Code original:")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    
    if transformer.can_transform(sample_code):
        transformed = transformer.transform(sample_code)
        print("Code transformé:")
        print(transformed)
    else:
        print("Aucune transformation nécessaire")
