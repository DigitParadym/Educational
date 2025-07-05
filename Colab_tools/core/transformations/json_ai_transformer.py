#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin de Transformation : JSON-AI Instructions
Applique des transformations basées sur des instructions JSON générées par IA
"""

import ast
import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, Any, List

# Ajouter le chemin pour importer BaseTransformer
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from base_transformer import BaseTransformer
from core.base_transformer import BaseTransformer

class JsonAITransformer(BaseTransformer):
    """
    Transformer qui applique des instructions JSON générées par IA.
    Sécurisé : seules les instructions prédéfinies sont autorisées.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Transformations JSON-AI"
        self.description = "Applique des transformations basées sur instructions JSON IA"
        self.version = "1.0"
        self.author = "Système AST Modulaire"
        self.json_instructions = None
        self.transformations_applied = 0
        
        # Actions sécurisées autorisées
        self.allowed_actions = {
            'replace_text': self._action_replace_text,
            'replace_function_call': self._action_replace_function_call,
            'add_import': self._action_add_import,
            'add_docstring': self._action_add_docstring,
            'rename_variable': self._action_rename_variable,
            'add_comment': self._action_add_comment,
            'remove_print': self._action_remove_print,
            'convert_print_to_logging': self._action_convert_print_to_logging
        }
    
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
        Vérifie si des instructions JSON sont disponibles.
        Cette méthode sera appelée différemment pour le mode JSON.
        """
        return True  # Toujours applicable, les instructions seront vérifiées plus tard
    
    def load_json_instructions(self, json_file_path):
        """
        Charge les instructions depuis un fichier JSON.
        
        Args:
            json_file_path (str): Chemin vers le fichier JSON
            
        Returns:
            bool: True si le chargement réussit
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_instructions = json.load(f)
            
            # Validation du format JSON
            if not self._validate_json_structure():
                print("X Format JSON invalide")
                return False
            
            print(f"+ Instructions JSON chargées: {len(self.json_instructions.get('transformations', []))} transformation(s)")
            return True
            
        except json.JSONDecodeError as e:
            print(f"X Erreur JSON: {e}")
            return False
        except Exception as e:
            print(f"X Erreur chargement JSON: {e}")
            return False
    
    def _validate_json_structure(self):
        """Valide la structure du JSON."""
        if not isinstance(self.json_instructions, dict):
            return False
        
        if 'transformations' not in self.json_instructions:
            return False
        
        if not isinstance(self.json_instructions['transformations'], list):
            return False
        
        # Valider chaque transformation
        for transformation in self.json_instructions['transformations']:
            if not isinstance(transformation, dict):
                return False
            if 'action' not in transformation:
                return False
            if transformation['action'] not in self.allowed_actions:
                print(f"! Action non autorisée: {transformation['action']}")
                return False
        
        return True
    
    def transform(self, code_source):
        """
        Applique les transformations JSON au code source.
        
        Args:
            code_source (str): Code source original
            
        Returns:
            str: Code source transformé
        """
        if not self.json_instructions:
            print("X Aucune instruction JSON chargée")
            return code_source
        
        try:
            self.transformations_applied = 0
            modified_code = code_source
            
            print(f"+ Application de {len(self.json_instructions['transformations'])} instruction(s)")
            
            # Appliquer chaque transformation
            for i, instruction in enumerate(self.json_instructions['transformations'], 1):
                action = instruction['action']
                
                if action in self.allowed_actions:
                    print(f"  [{i}] {action}")
                    modified_code = self.allowed_actions[action](modified_code, instruction)
                    self.transformations_applied += 1
                else:
                    print(f"  [{i}] Action ignorée (non autorisée): {action}")
            
            print(f"+ {self.transformations_applied} transformation(s) appliquée(s)")
            return modified_code
            
        except Exception as e:
            print(f"X Erreur transformation JSON: {e}")
            return code_source
    
    def _action_replace_text(self, code, instruction):
        """Remplace du texte simple."""
        old_text = instruction.get('from', '')
        new_text = instruction.get('to', '')
        
        if old_text and old_text in code:
            return code.replace(old_text, new_text)
        return code
    
    def _action_replace_function_call(self, code, instruction):
        """Remplace un appel de fonction."""
        old_function = instruction.get('old_function', '')
        new_function = instruction.get('new_function', '')
        
        if old_function and new_function:
            # Utiliser regex pour remplacer les appels de fonction
            pattern = re.compile(rf'\b{re.escape(old_function)}\s*\(')
            return pattern.sub(f'{new_function}(', code)
        return code
    
    def _action_add_import(self, code, instruction):
        """Ajoute un import."""
        module = instruction.get('module', '')
        import_type = instruction.get('type', 'import')  # 'import' ou 'from'
        
        if not module:
            return code
        
        lines = code.split('\n')
        
        # Trouver où insérer l'import
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                insert_pos = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                break
        
        # Créer la ligne d'import
        if import_type == 'from':
            items = instruction.get('items', [])
            if items:
                import_line = f"from {module} import {', '.join(items)}"
            else:
                import_line = f"import {module}"
        else:
            import_line = f"import {module}"
        
        # Vérifier si l'import existe déjà
        if not any(import_line in line for line in lines[:insert_pos + 5]):
            lines.insert(insert_pos, import_line)
        
        return '\n'.join(lines)
    
    def _action_add_docstring(self, code, instruction):
        """Ajoute un docstring à une fonction."""
        function_name = instruction.get('function', '')
        docstring_text = instruction.get('docstring', '')
        
        if not function_name or not docstring_text:
            return code
        
        try:
            tree = ast.parse(code)
            transformer = DocstringAdder(function_name, docstring_text)
            modified_tree = transformer.visit(tree)
            return ast.unparse(modified_tree)
        except:
            return code
    
    def _action_rename_variable(self, code, instruction):
        """Renomme une variable."""
        old_name = instruction.get('old_name', '')
        new_name = instruction.get('new_name', '')
        
        if old_name and new_name:
            # Renommage intelligent avec limites de mot
            pattern = re.compile(rf'\b{re.escape(old_name)}\b')
            return pattern.sub(new_name, code)
        return code
    
    def _action_add_comment(self, code, instruction):
        """Ajoute un commentaire."""
        line_number = instruction.get('line', 0)
        comment_text = instruction.get('comment', '')
        
        if line_number > 0 and comment_text:
            lines = code.split('\n')
            if line_number <= len(lines):
                lines.insert(line_number - 1, f"# {comment_text}")
                return '\n'.join(lines)
        return code
    
    def _action_remove_print(self, code, instruction):
        """Supprime les appels print()."""
        # Supprimer les lignes contenant uniquement print()
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('print(') and stripped.endswith(')'):
                # Remplacer par un commentaire
                indent = line[:len(line) - len(line.lstrip())]
                filtered_lines.append(f"{indent}# Removed: {stripped}")
            else:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _action_convert_print_to_logging(self, code, instruction):
        """Convertit print() en logging."""
        # Ajouter l'import logging si nécessaire
        if 'import logging' not in code:
            code = self._action_add_import(code, {'module': 'logging'})
        
        # Remplacer print( par logging.info(
        return re.sub(r'\bprint\s*\(', 'logging.info(', code)
    
    def preview_changes(self, code_source):
        """
        Prévisualise les changements sans les appliquer.
        """
        if not self.json_instructions:
            return {
                'applicable': False,
                'description': 'Aucune instruction JSON chargée',
                'estimated_changes': 0
            }
        
        transformations = self.json_instructions.get('transformations', [])
        valid_actions = [t for t in transformations if t.get('action') in self.allowed_actions]
        
        return {
            'applicable': len(valid_actions) > 0,
            'description': f"Appliquera {len(valid_actions)} instruction(s) JSON",
            'estimated_changes': len(valid_actions),
            'details': {
                'total_instructions': len(transformations),
                'valid_instructions': len(valid_actions),
                'actions': [t.get('action') for t in valid_actions]
            }
        }


class DocstringAdder(ast.NodeTransformer):
    """Helper pour ajouter des docstrings à des fonctions spécifiques."""
    
    def __init__(self, function_name, docstring_text):
        self.function_name = function_name
        self.docstring_text = docstring_text
    
    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            # Vérifier si la fonction a déjà un docstring
            if (not node.body or 
                not isinstance(node.body[0], ast.Expr) or 
                not isinstance(node.body[0].value, ast.Constant)):
                
                # Ajouter le docstring
                docstring_node = ast.Expr(value=ast.Constant(value=self.docstring_text))
                node.body.insert(0, docstring_node)
        
        self.generic_visit(node)
        return node


# Exemple d'utilisation et de test
if __name__ == "__main__":
    # JSON d'exemple
    example_json = {
        "transformations": [
            {
                "action": "add_import",
                "module": "logging"
            },
            {
                "action": "convert_print_to_logging"
            },
            {
                "action": "add_docstring",
                "function": "main",
                "docstring": "Fonction principale du programme."
            }
        ]
    }
    
    # Code de test
    test_code = '''
def main():
    print("Hello World")
    print("This is a test")

def autre_fonction():
    print("Another function")
'''
    
    # Tester la transformation
    transformer = JsonAITransformer()
    
    print("=== TEST TRANSFORMATION JSON-AI ===")
    print("Code original:")
    print(test_code)
    
    # Simuler le chargement JSON
    transformer.json_instructions = example_json
    
    print("\n" + "="*50)
    print("Instructions JSON:")
    print(json.dumps(example_json, indent=2))
    
    print("\n" + "="*50)
    print("Application des transformations:")
    transformed_code = transformer.transform(test_code)
    
    print("\n" + "="*50)
    print("Code transformé:")
    print(transformed_code)
