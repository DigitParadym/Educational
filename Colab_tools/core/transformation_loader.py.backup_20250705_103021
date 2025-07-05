#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chargeur Dynamique de Transformations - Version Enhanced
Decouvre et charge dynamiquement les plugins de transformation
"""

import os
import sys
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Optional, List
from .base_transformer import BaseTransformer

class TransformationLoader:
    """
    Decouvre et charge dynamiquement les plugins de transformation
    depuis le dossier 'transformations'.
    """
    
    def __init__(self, transformations_dir="core/transformations"):
        self.transformations_dir = Path(transformations_dir)
        self.plugins: Dict[str, BaseTransformer] = {}
        self.discover_plugins()
    
    def discover_plugins(self):
        """Scanne le dossier des plugins et charge les transformations valides."""
        if not self.transformations_dir.exists():
            print(f"! Dossier {self.transformations_dir} non trouve")
            return
        
        # Ajouter le chemin au sys.path si necessaire
        parent_dir = str(self.transformations_dir.parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        plugins_loaded = 0
        
        for file_path in self.transformations_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            module_name = file_path.stem
            try:
                # Importation dynamique du module avec spec
                spec = importlib.util.spec_from_file_location(
                    f"core.transformations.{module_name}", 
                    file_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Chercher la classe qui herite de BaseTransformer
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTransformer) and 
                            obj is not BaseTransformer):
                            
                            # Instancier le plugin
                            try:
                                instance = obj()
                                metadata = instance.get_metadata()
                                self.plugins[module_name] = instance
                                print(f"+ Plugin charge : {metadata['name']} v{metadata['version']}")
                                plugins_loaded += 1
                                break
                            except Exception as e:
                                print(f"! Erreur instanciation {name}: {e}")
                
            except Exception as e:
                print(f"! Erreur chargement plugin {module_name}: {e}")
        
        if plugins_loaded == 0:
            print(f"! Aucune transformation trouvee dans {self.transformations_dir}")
        else:
            print(f"+ {plugins_loaded} plugin(s) charge(s) avec succes")
    
    def get_transformation(self, name: str) -> Optional[BaseTransformer]:
        """Retourne une instance du plugin demande."""
        return self.plugins.get(name)
    
    def list_transformations(self) -> List[str]:
        """Liste tous les noms de plugins charges."""
        return list(self.plugins.keys())
    
    def get_transformation_metadata(self) -> Dict[str, Dict]:
        """Retourne les metadonnees de tous les plugins charges."""
        return {name: plugin.get_metadata() for name, plugin in self.plugins.items()}
    
    def reload_plugins(self):
        """Recharge tous les plugins (utile pour le developpement)."""
        print("Rechargement des plugins...")
        self.plugins.clear()
        
        # Nettoyer les modules caches
        modules_to_remove = [
            mod for mod in sys.modules.keys() 
            if mod.startswith('core.transformations.')
        ]
        for mod in modules_to_remove:
            del sys.modules[mod]
        
        # Recharger
        self.discover_plugins()
        return len(self.plugins)
    
    def test_transformation(self, name: str, code_source: str) -> tuple[bool, str]:
        """Teste une transformation sur du code."""
        transformer = self.get_transformation(name)
        if not transformer:
            return False, f"Transformation '{name}' non trouvee"
        
        try:
            applicable = transformer.can_transform(code_source)
            if applicable:
                metadata = transformer.get_metadata()
                return True, f"Transformation '{metadata['name']}' applicable"
            else:
                return False, f"Transformation non applicable"
        except Exception as e:
            return False, f"Erreur test: {e}"
    
    def get_plugin_info(self, name: str) -> Optional[Dict]:
        """Retourne les informations detaillees d'un plugin."""
        transformer = self.get_transformation(name)
        if not transformer:
            return None
        
        metadata = transformer.get_metadata()
        return {
            'metadata': metadata,
            'imports_required': transformer.get_imports_required(),
            'has_config': bool(transformer.get_config_code().strip()),
            'class_name': transformer.__class__.__name__,
            'module_path': transformer.__class__.__module__
        }
