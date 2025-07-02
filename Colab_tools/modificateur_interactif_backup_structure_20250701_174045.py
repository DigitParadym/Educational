#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OUTIL DE REFONTE DE CODE PYTHON PAR AST - VERSION MINIMALE FONCTIONNELLE
Cree automatiquement pour remplacer le fichier incomplet
"""

import ast
import os
import sys
import datetime
import json
from typing import List, Dict, Any, Optional

# Detection d'environnement
COLAB_ENV = False
VSCODE_ENV = False

try:
    import google.colab
    from google.colab import files
    COLAB_ENV = True
    print("*** Environnement Google Colab detecte ***")
except ImportError:
    pass

try:
    if 'VSCODE_PID' in os.environ or 'JUPYTER_SERVER_ROOT' in os.environ:
        VSCODE_ENV = True
        print("*** Environnement VSCode/Jupyter detecte ***")
except:
    pass

if not COLAB_ENV and not VSCODE_ENV:
    print("*** Environnement Terminal detecte ***")

# ==============================================================================
# UTILITAIRES GENERAUX
# ==============================================================================

def format_taille(taille_bytes):
    """Formate une taille en bytes en format lisible."""
    for unite in ['B', 'KB', 'MB', 'GB']:
        if taille_bytes < 1024.0:
            return f"{taille_bytes:.1f} {unite}"
        taille_bytes /= 1024.0
    return f"{taille_bytes:.1f} TB"

# ==============================================================================
# ANALYSEUR DE CODE SIMPLIFIE
# ==============================================================================

class AnalyseurCode:
    """Analyseur de code Python utilisant AST."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Remet a zero l'analyseur."""
        self.fonctions = []
        self.classes = []
        self.imports = []
        self.print_calls = []
        self.erreurs = []
    
    def analyser_code(self, code_source):
        """Analyse le code source Python."""
        try:
            self.reset()
            arbre = ast.parse(code_source)
            
            for noeud in ast.walk(arbre):
                if isinstance(noeud, ast.FunctionDef):
                    self.fonctions.append({'nom': noeud.name, 'ligne': noeud.lineno})
                elif isinstance(noeud, ast.ClassDef):
                    self.classes.append({'nom': noeud.name, 'ligne': noeud.lineno})
                elif isinstance(noeud, ast.Call):
                    if (isinstance(noeud.func, ast.Name) and noeud.func.id == 'print'):
                        self.print_calls.append({'ligne': noeud.lineno})
            
            return True
            
        except Exception as e:
            self.erreurs.append(f"Erreur analyse: {e}")
            return False
    
    def obtenir_rapport(self):
        """Genere un rapport d'analyse."""
        return {
            'fonctions': len(self.fonctions),
            'classes': len(self.classes),
            'print_calls': len(self.print_calls),
            'erreurs': len(self.erreurs)
        }

# ==============================================================================
# TRANSFORMATEUR AST SIMPLIFIE
# ==============================================================================

class TransformateurAST(ast.NodeTransformer):
    """Transformateur AST pour convertir print() en logging."""
    
    def __init__(self):
        self.transformations = 0
    
    def visit_Call(self, node):
        """Visite les appels de fonction."""
        self.generic_visit(node)
        
        if (isinstance(node.func, ast.Name) and node.func.id == 'print'):
            self.transformations += 1
            # Creer l'appel logging.info()
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='logging', ctx=ast.Load()),
                    attr='info',
                    ctx=ast.Load()
                ),
                args=node.args,
                keywords=node.keywords
            )
        
        return node

# ==============================================================================
# ORCHESTRATEUR PRINCIPAL SIMPLIFIE
# ==============================================================================

class OrchestrateurAST:
    """Orchestrateur principal pour les transformations AST."""
    
    def __init__(self, mode_colab=False):
        self.mode_colab = mode_colab
        self.analyseur = AnalyseurCode()
        self.historique = []
        
        # NOUVEAU: Chargeur de transformations modulaires
        self.transformation_loader = None
        self._init_modular_system()
    
    def _init_modular_system(self):
        """Initialise le systeme modulaire."""
        try:
            from core.transformation_loader import TransformationLoader
            self.transformation_loader = TransformationLoader()
            plugins_info = self.transformation_loader.get_transformation_metadata()
            if plugins_info:
                print(f"+ Systeme modulaire actif: {len(plugins_info)} transformation(s)")
                for name, metadata in plugins_info.items():
                    print(f"  - {metadata['name']} v{metadata['version']}")
            else:
                print("+ Systeme modulaire actif (aucune transformation dans core/)")
        except ImportError:
            print("! Systeme modulaire non disponible (dossier core/ manquant)")
        except Exception as e:
            print(f"! Erreur systeme modulaire: {e}")
    
    def transformation_simple(self, fichier_source, fichier_sortie):
        """Transformation simple print() -> logging.info()"""
        try:
            with open(fichier_source, 'r', encoding='utf-8') as f:
                code_source = f.read()
            
            # Analyser
            if not self.analyseur.analyser_code(code_source):
                print("X Erreur analyse")
                return False
            
            rapport = self.analyseur.obtenir_rapport()
            print(f"Analyse: {rapport['print_calls']} print() detectes")
            
            # Transformer
            arbre = ast.parse(code_source)
            transformateur = TransformateurAST()
            arbre_transforme = transformateur.visit(arbre)
            code_modifie = ast.unparse(arbre_transforme)
            
            # Ajouter import logging
            if transformateur.transformations > 0:
                code_final = "import logging\n\n" + code_modifie
            else:
                code_final = code_modifie
            
            # Sauvegarder
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                f.write(code_final)
            
            print(f"+ Transformation reussie: {transformateur.transformations} modifications")
            return True
            
        except Exception as e:
            print(f"X Erreur: {e}")
            return False
    
    def lister_transformations_modulaires(self):
        """Liste les transformations modulaires si disponibles."""
        if not self.transformation_loader:
            return []
        
        transformations = []
        plugins_metadata = self.transformation_loader.get_transformation_metadata()
        for plugin_name, metadata in plugins_metadata.items():
            transformations.append({
                'name': plugin_name,
                'display_name': metadata['name'],
                'description': metadata['description'],
                'version': metadata['version']
            })
        return transformations

# ==============================================================================
# BROWSER DE FICHIERS SIMPLIFIE
# ==============================================================================

def browser_fichier_simple():
    """Browser simple pour selectionner un fichier Python."""
    repertoire_actuel = os.getcwd()
    fichiers_python = [f for f in os.listdir(repertoire_actuel) if f.endswith('.py')]
    
    if not fichiers_python:
        print("Aucun fichier Python trouve dans le repertoire actuel")
        return None
    
    print("Fichiers Python disponibles:")
    for i, fichier in enumerate(fichiers_python, 1):
        print(f"{i}. {fichier}")
    
    try:
        choix = int(input(f"Choisissez un fichier (1-{len(fichiers_python)}): ")) - 1
        if 0 <= choix < len(fichiers_python):
            return os.path.join(repertoire_actuel, fichiers_python[choix])
    except:
        pass
    
    return None

# ==============================================================================
# FONCTIONS PRINCIPALES
# ==============================================================================

def demo_simple():
    """Demonstration simple."""
    print("*** DEMONSTRATION SIMPLE - Outil AST ***")
    print("=" * 40)
    
    fichier = browser_fichier_simple()
    if not fichier:
        print("Aucun fichier selectionne")
        return
    
    print(f"Fichier selectionne: {os.path.basename(fichier)}")
    
    # Generer nom de sortie
    base, ext = os.path.splitext(fichier)
    fichier_sortie = base + "_transforme" + ext
    
    # Transformer
    orchestrateur = OrchestrateurAST()
    if orchestrateur.transformation_simple(fichier, fichier_sortie):
        print(f"+ Fichier transforme: {fichier_sortie}")
    else:
        print("X Transformation echouee")

def menu_principal():
    """Menu principal simplifie."""
    print("*** OUTIL AST - VERSION MINIMALE ***")
    print("=" * 40)
    print("1. Demonstration simple")
    print("2. Tester systeme modulaire")
    print("3. Quitter")
    
    choix = input("Votre choix (1-3): ").strip()
    return choix

def main():
    """Point d'entree principal."""
    try:
        # Essayer l'interface GUI
        from composants_browser.interface_gui_principale import InterfaceAST
        print(">> Lancement interface GUI...")
        app = InterfaceAST()
        app.run()
    except ImportError:
        print("Interface GUI non disponible, mode texte...")
        
        while True:
            choix = menu_principal()
            
            if choix == "1":
                demo_simple()
            elif choix == "2":
                orchestrateur = OrchestrateurAST()
                transformations = orchestrateur.lister_transformations_modulaires()
                if transformations:
                    print("Transformations modulaires disponibles:")
                    for t in transformations:
                        print(f"  - {t['display_name']}: {t['description']}")
                else:
                    print("Aucune transformation modulaire disponible")
                input("Appuyez sur Entree...")
            elif choix == "3":
                print("*** DEMO TRANSFORMATION MODULAIRE ***")
                orchestrateur = OrchestrateurAST()
                orchestrateur.demo_modulaire()
                input("\nAppuyez sur Entree pour continuer...")
            elif choix == "4":
                break
            else:
                print("Choix invalide (1-4)")

if __name__ == "__main__":
    main()

    def appliquer_transformation_modulaire(self, fichier_source, fichier_sortie, transformation_name):
        """
        Applique une transformation modulaire du systeme core/.
        
        Args:
            fichier_source (str): Chemin vers le fichier source
            fichier_sortie (str): Chemin vers le fichier de sortie
            transformation_name (str): Nom technique du plugin a utiliser
            
        Returns:
            bool: True si la transformation a reussi, False sinon
        """
        if not self.transformation_loader:
            print("X Systeme modulaire non disponible")
            return False
        
        # Recuperer le plugin de transformation
        transformer = self.transformation_loader.get_transformation(transformation_name)
        if not transformer:
            print(f"X Transformation '{transformation_name}' non trouvee")
            available = self.transformation_loader.list_transformations()
            print(f"Transformations disponibles: {', '.join(available)}")
            return False
        
        try:
            metadata = transformer.get_metadata()
            print(f"Transformation modulaire : {metadata['name']} v{metadata['version']}")
            print(f"Description : {metadata['description']}")
            print(f"Auteur : {metadata['author']}")
            print("-" * 50)
            
            # Lecture du fichier source
            with open(fichier_source, 'r', encoding='utf-8') as f:
                code_source = f.read()
            
            # Verifier si la transformation est applicable
            if not transformer.can_transform(code_source):
                print(f"! Transformation '{metadata['name']}' non applicable a ce code")
                
                # Optionnel: afficher un apercu pour diagnostic
                try:
                    if hasattr(transformer, 'preview_changes'):
                        preview = transformer.preview_changes(code_source)
                        print(f"Details: {preview.get('description', 'Aucun detail')}")
                except:
                    pass
                    
                return False
            
            # Analyser le code avant transformation
            if self.analyseur.analyser_code(code_source):
                rapport_avant = self.analyseur.obtenir_rapport()
                print(f"+ Analyse pre-transformation: {rapport_avant['fonctions']} fonctions, {rapport_avant['classes']} classes")
            
            # APPLIQUER LA TRANSFORMATION - Coeur du systeme modulaire
            print(f"+ Application de la transformation '{metadata['name']}'...")
            code_transforme = transformer.transform(code_source)
            
            if code_transforme == code_source:
                print("! Aucune modification apportee au code")
                # Peut quand meme etre considere comme un succes
            
            # Ajouter les imports requis
            imports_requis = transformer.get_imports_required()
            if imports_requis:
                code_transforme = self._ajouter_imports_modulaire(code_transforme, imports_requis)
                print(f"+ Imports ajoutes: {', '.join(imports_requis)}")
            
            # Ajouter la configuration
            config_code = transformer.get_config_code()
            if config_code and config_code.strip():
                code_transforme = self._inserer_config_modulaire(code_transforme, config_code)
                print(f"+ Configuration ajoutee")
            
            # Ajouter l'en-tete specialise
            code_final = self._ajouter_entete_modulaire(code_transforme, fichier_source, transformer)
            
            # Sauvegarder le fichier transforme
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                f.write(code_final)
            
            print(f"+ Transformation '{metadata['name']}' appliquee avec succes!")
            print(f"+ Fichier de sortie : {fichier_sortie}")
            
            # Enregistrement dans l'historique
            self.historique.append({
                'timestamp': datetime.datetime.now().isoformat(),
                'source': fichier_source,
                'sortie': fichier_sortie,
                'transformation': transformation_name,
                'transformation_display_name': metadata['name'],
                'transformation_version': metadata['version'],
                'type': 'modulaire',
                'metadata': metadata
            })
            
            return True
            
        except Exception as e:
            print(f"X Erreur transformation modulaire: {e}")
            import traceback
            traceback.print_exc()  # Pour le debugging
            return False
    
    def _ajouter_imports_modulaire(self, code, imports_requis):
        """Ajoute les imports requis de maniere intelligente."""
        lignes = code.split('\n')
        position_insertion = 0
        
        # Trouver la fin des imports existants
        for i, ligne in enumerate(lignes):
            if ligne.strip().startswith(('import ', 'from ')):
                position_insertion = i + 1
            elif ligne.strip() and not ligne.strip().startswith('#'):
                break
        
        # Ajouter les nouveaux imports
        for import_module in imports_requis:
            import_line = f"import {import_module}"
            if not any(import_line in ligne for ligne in lignes[:position_insertion]):
                lignes.insert(position_insertion, import_line)
                position_insertion += 1
        
        return '\n'.join(lignes)
    
    def _inserer_config_modulaire(self, code, config_code):
        """Insere le code de configuration apres les imports."""
        lignes = code.split('\n')
        position_insertion = 0
        
        # Trouver la fin des imports
        for i, ligne in enumerate(lignes):
            if ligne.strip().startswith(('import ', 'from ')):
                position_insertion = i + 1
            elif ligne.strip() and not ligne.strip().startswith('#'):
                break
        
        # Inserer la configuration
        config_lignes = config_code.strip().split('\n')
        for ligne in reversed(config_lignes):
            lignes.insert(position_insertion, ligne)
        
        return '\n'.join(lignes)
    
    def _ajouter_entete_modulaire(self, code, fichier_source, transformer):
        """Ajoute un en-tete specialise pour transformation modulaire."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = transformer.get_metadata()
        
        entete = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
FICHIER TRANSFORME PAR SYSTEME MODULAIRE
==============================================================================

Fichier original : {os.path.basename(fichier_source)}
Plugin utilise : {metadata['name']} v{metadata['version']}
Description : {metadata['description']}
Auteur plugin : {metadata['author']}
Date transformation : {timestamp}
Systeme : Refonte AST v2.4 - Systeme Modulaire

Modifications appliquees :
- {metadata['description']}
- Imports automatiques : {', '.join(transformer.get_imports_required()) if transformer.get_imports_required() else 'Aucun'}
- Configuration : {'Oui' if transformer.get_config_code() and transformer.get_config_code().strip() else 'Non'}

Plugin classe : {transformer.__class__.__name__}
Plugin module : {transformer.__class__.__module__}
==============================================================================
"""

'''
        return entete + code
    
    def demo_modulaire(self):
        """Demonstration du systeme modulaire."""
        print("*** DEMONSTRATION SYSTEME MODULAIRE ***")
        print("=" * 45)
        
        # Lister les transformations disponibles
        transformations = self.lister_transformations_modulaires()
        
        if not transformations:
            print("X Aucune transformation modulaire disponible")
            print("Verifiez que le dossier core/transformations/ existe")
            print("et contient des fichiers de transformation valides")
            return
        
        print(f"Transformations disponibles: {len(transformations)}")
        for i, t in enumerate(transformations, 1):
            print(f"{i}. {t['display_name']} - {t['description']}")
        
        # Selectionner un fichier a transformer
        print("\nSelection du fichier a transformer...")
        fichier_source = browser_fichier_simple()
        if not fichier_source:
            print("Aucun fichier selectionne")
            return
        
        print(f"Fichier selectionne: {os.path.basename(fichier_source)}")
        
        # Choisir une transformation
        try:
            choix = int(input(f"\nChoisissez une transformation (1-{len(transformations)}): ")) - 1
            if 0 <= choix < len(transformations):
                transformation = transformations[choix]
                transformation_name = transformation['name']
                
                # Generer nom de fichier de sortie
                base, ext = os.path.splitext(fichier_source)
                fichier_sortie = f"{base}_{transformation_name}_modulaire{ext}"
                
                # Appliquer la transformation
                print(f"\nApplication de: {transformation['display_name']}")
                success = self.appliquer_transformation_modulaire(
                    fichier_source, fichier_sortie, transformation_name
                )
                
                if success:
                    print("\n+ Transformation modulaire reussie!")
                    print(f"+ Fichier genere: {fichier_sortie}")
                    
                    # Proposer de voir les differences
                    voir_diff = input("\nVoir un apercu du fichier transforme? (o/N): ").strip().lower()
                    if voir_diff in ['o', 'oui', 'y', 'yes']:
                        try:
                            with open(fichier_sortie, 'r', encoding='utf-8') as f:
                                lignes = f.readlines()
                            print("\n--- APERCU (20 premieres lignes) ---")
                            for i, ligne in enumerate(lignes[:20], 1):
                                print(f"{i:2d}: {ligne.rstrip()}")
                            if len(lignes) > 20:
                                print(f"... et {len(lignes) - 20} lignes suivantes")
                        except Exception as e:
                            print(f"Erreur lecture apercu: {e}")
                else:
                    print("\nX Transformation modulaire echouee")
            else:
                print("Choix invalide (1-4)")
                
        except ValueError:
            print("Choix invalide")
        except Exception as e:
            print(f"Erreur: {e}")
