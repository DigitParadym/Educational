#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
OUTIL DE REFONTE DE CODE PYTHON PAR AST - VERSION 2.4 INTÉGRÉE
==============================================================================

Auteur: Assistant IA Claude
Créé: Octobre 2024
Mis à jour: Décembre 2024

FONCTIONNALITÉS:
- Transformation automatique de print() en logging
- Interface GUI moderne pour sélection multiple
- Support JSON AI pour transformations pilotées par IA
- Traitement en lot avec fallback intelligent
- Gestion adaptée selon l'environnement (Colab/VSCode/Terminal)
- Session interactive pour recettes personnalisées

ARCHITECTURE:
- OrchestrateurAST: Gestionnaire principal des transformations
- AnalyseurCode: Analyse statique du code source
- TransformateurAST: Application des modifications via AST
- Interface GUI: Sélection moderne de fichiers/dossiers
- Fallback Browser: Interface texte de secours
"""

import ast
import os
import sys
import datetime
import json
import time
import inspect
import shutil
import subprocess
import platform
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path

# Détection d'environnement
COLAB_ENV = False
VSCODE_ENV = False

try:
    import google.colab
    from google.colab import files
    COLAB_ENV = True
    print("*** Environnement Google Colab détecté ***")
except ImportError:
    pass

try:
    if 'VSCODE_PID' in os.environ or 'JUPYTER_SERVER_ROOT' in os.environ:
        VSCODE_ENV = True
        print("*** Environnement VSCode/Jupyter détecté ***")
except:
    pass

if not COLAB_ENV and not VSCODE_ENV:
    print("*** Environnement Terminal détecté ***")

# ==============================================================================
# UTILITAIRES GÉNÉRAUX
# ==============================================================================

def format_taille(taille_bytes):
    """Formate une taille en bytes en format lisible."""
    for unite in ['B', 'KB', 'MB', 'GB']:
        if taille_bytes < 1024.0:
            return f"{taille_bytes:.1f} {unite}"
        taille_bytes /= 1024.0
    return f"{taille_bytes:.1f} TB"

def afficher_diff_simple(fichier1, fichier2):
    """Affiche les différences entre deux fichiers de manière simple."""
    try:
        with open(fichier1, 'r', encoding='utf-8') as f1:
            lignes1 = f1.readlines()
        with open(fichier2, 'r', encoding='utf-8') as f2:
            lignes2 = f2.readlines()
        
        print("*** APERÇU DES DIFFÉRENCES ***")
        print("=" * 40)
        
        differences = 0
        for i, (ligne1, ligne2) in enumerate(zip(lignes1, lignes2), 1):
            if ligne1 != ligne2:
                differences += 1
                if differences <= 5:  # Limiter l'affichage
                    print(f"Ligne {i}:")
                    print(f"  Avant: {ligne1.strip()}")
                    print(f"  Après: {ligne2.strip()}")
                    print()
        
        if differences > 5:
            print(f"... et {differences - 5} autres différences")
        
        print(f"Total: {differences} lignes modifiées")
        
    except Exception as e:
        print(f"Erreur lors de la comparaison : {e}")

# ==============================================================================
# ANALYSEUR DE CODE
# ==============================================================================

class AnalyseurCode:
    """Analyseur de code Python utilisant AST."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Remet à zéro l'analyseur."""
        self.fonctions = []
        self.classes = []
        self.imports = []
        self.variables_globales = []
        self.print_calls = []
        self.erreurs = []
    
    def analyser_fichier(self, chemin_fichier):
        """Analyse un fichier Python complet."""
        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                contenu = f.read()
            
            return self.analyser_code(contenu)
        except Exception as e:
            self.erreurs.append(f"Erreur lecture fichier : {e}")
            return False
    
    def analyser_code(self, code_source):
        """Analyse le code source Python."""
        try:
            self.reset()
            arbre = ast.parse(code_source)
            
            for noeud in ast.walk(arbre):
                if isinstance(noeud, ast.FunctionDef):
                    self.fonctions.append({
                        'nom': noeud.name,
                        'ligne': noeud.lineno,
                        'args': [arg.arg for arg in noeud.args.args],
                        'decorateurs': [ast.unparse(d) for d in noeud.decorator_list]
                    })
                
                elif isinstance(noeud, ast.ClassDef):
                    self.classes.append({
                        'nom': noeud.name,
                        'ligne': noeud.lineno,
                        'bases': [ast.unparse(base) for base in noeud.bases],
                        'decorateurs': [ast.unparse(d) for d in noeud.decorator_list]
                    })
                
                elif isinstance(noeud, (ast.Import, ast.ImportFrom)):
                    if isinstance(noeud, ast.Import):
                        for alias in noeud.names:
                            self.imports.append({
                                'type': 'import',
                                'module': alias.name,
                                'alias': alias.asname,
                                'ligne': noeud.lineno
                            })
                    else:
                        for alias in noeud.names:
                            self.imports.append({
                                'type': 'from',
                                'module': noeud.module,
                                'nom': alias.name,
                                'alias': alias.asname,
                                'ligne': noeud.lineno
                            })
                
                elif isinstance(noeud, ast.Call):
                    if (isinstance(noeud.func, ast.Name) and noeud.func.id == 'print'):
                        self.print_calls.append({
                            'ligne': noeud.lineno,
                            'args': len(noeud.args),
                            'keywords': [kw.arg for kw in noeud.keywords]
                        })
            
            return True
            
        except SyntaxError as e:
            self.erreurs.append(f"Erreur syntaxe ligne {e.lineno}: {e.msg}")
            return False
        except Exception as e:
            self.erreurs.append(f"Erreur analyse: {e}")
            return False
    
    def extraire_fonctions(self, code_source):
        """Extrait les fonctions du code."""
        if self.analyser_code(code_source):
            return self.fonctions
        return []
    
    def extraire_classes(self, code_source):
        """Extrait les classes du code."""
        if self.analyser_code(code_source):
            return self.classes
        return []
    
    def compter_lignes_par_type(self, code_source):
        """Compte les différents types de lignes."""
        lignes = code_source.split('\n')
        stats = {
            'total': len(lignes),
            'vides': 0,
            'commentaires': 0,
            'code': 0
        }
        
        for ligne in lignes:
            ligne_stripped = ligne.strip()
            if not ligne_stripped:
                stats['vides'] += 1
            elif ligne_stripped.startswith('#'):
                stats['commentaires'] += 1
            else:
                stats['code'] += 1
        
        return stats
    
    def obtenir_rapport(self):
        """Génère un rapport d'analyse."""
        rapport = {
            'fonctions': len(self.fonctions),
            'classes': len(self.classes),
            'imports': len(self.imports),
            'print_calls': len(self.print_calls),
            'erreurs': len(self.erreurs)
        }
        
        if self.print_calls:
            rapport['print_lines'] = [call['ligne'] for call in self.print_calls]
        
        return rapport

# ==============================================================================
# TRANSFORMATEUR AST
# ==============================================================================

class TransformateurAST(ast.NodeTransformer):
    """Transformateur AST pour convertir print() en logging."""
    
    def __init__(self):
        self.transformations = 0
        self.imports_ajoutes = set()
        self.require_logging = False
    
    def visit_Call(self, node):
        """Visite les appels de fonction."""
        self.generic_visit(node)
        
        # Transformer print() en logging.info()
        if (isinstance(node.func, ast.Name) and 
            node.func.id == 'print' and 
            not self._est_dans_commentaire(node)):
            
            self.transformations += 1
            self.require_logging = True
            
            # Créer l'appel logging.info()
            nouveau_noeud = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='logging', ctx=ast.Load()),
                    attr='info',
                    ctx=ast.Load()
                ),
                args=node.args,
                keywords=node.keywords
            )
            
            return nouveau_noeud
        
        return node
    
    def _est_dans_commentaire(self, node):
        """Vérifie si le nœud est dans un commentaire."""
        # Logique simplifiée - peut être améliorée
        return False
    
    def obtenir_statistiques(self):
        """Retourne les statistiques de transformation."""
        return {
            'transformations': self.transformations,
            'require_logging': self.require_logging,
            'imports_ajoutes': list(self.imports_ajoutes)
        }

# ==============================================================================
# GESTIONNAIRE DE RECETTES
# ==============================================================================

class GestionnaireRecettes:
    """Gestionnaire des recettes de transformation."""
    
    def __init__(self):
        self.recettes = {}
        self.charger_recettes_par_defaut()
    
    def charger_recettes_par_defaut(self):
        """Charge les recettes de transformation par défaut."""
        self.recettes['print_to_logging'] = {
            'nom': 'Conversion Print vers Logging',
            'description': 'Convertit les appels print() en logging.info()',
            'transformations': ['print_to_logging'],
            'imports_requis': ['logging'],
            'config_logging': True
        }
        
        self.recettes['base_refonte'] = {
            'nom': 'Refonte de Base',
            'description': 'Refonte standard avec logging et en-tête',
            'transformations': ['print_to_logging', 'add_header'],
            'imports_requis': ['logging'],
            'config_logging': True,
            'header': True
        }
    
    def obtenir_recette(self, nom):
        """Obtient une recette par son nom."""
        return self.recettes.get(nom, {})
    
    def lister_recettes(self):
        """Liste toutes les recettes disponibles."""
        return list(self.recettes.keys())

# ==============================================================================
# ORCHESTRATEUR PRINCIPAL
# ==============================================================================

class OrchestrateurAST:
    """Orchestrateur principal pour les transformations AST."""
    
    def __init__(self, mode_colab=False):
        self.mode_colab = mode_colab
        self.analyseur = AnalyseurCode()
        self.gestionnaire_recettes = GestionnaireRecettes()
        self.historique = []
        self.session_active = False
    
    def appliquer_recette(self, fichier_source, fichier_sortie, nom_recette='base_refonte'):
        """Applique une recette de transformation à un fichier."""
        try:
            print(f"Transformation : {os.path.basename(fichier_source)}")
            print(f"Recette : {nom_recette}")
            print("-" * 40)
            
            # Lecture du fichier source
            with open(fichier_source, 'r', encoding='utf-8') as f:
                code_source = f.read()
            
            # Analyse préliminaire
            if not self.analyseur.analyser_code(code_source):
                print("X Erreur lors de l'analyse du code source")
                for erreur in self.analyseur.erreurs:
                    print(f"  • {erreur}")
                return False
            
            # Statistiques avant transformation
            stats_avant = self.analyseur.obtenir_rapport()
            print(f"• Print() détectés : {stats_avant['print_calls']}")
            print(f"• Fonctions : {stats_avant['fonctions']}")
            print(f"• Classes : {stats_avant['classes']}")
            
            # Transformation AST
            try:
                arbre = ast.parse(code_source)
                transformateur = TransformateurAST()
                arbre_transforme = transformateur.visit(arbre)
                
                # Statistiques de transformation
                stats_transform = transformateur.obtenir_statistiques()
                print(f"• Transformations appliquées : {stats_transform['transformations']}")
                
                # Génération du code modifié
                code_modifie = ast.unparse(arbre_transforme)
                
                # Ajout des imports et configuration si nécessaire
                if stats_transform['require_logging']:
                    code_modifie = self._ajouter_imports_et_config(code_modifie)
                
                # Ajout de l'en-tête
                code_final = self._ajouter_entete(code_modifie, fichier_source, nom_recette)
                
                # Écriture du fichier de sortie
                with open(fichier_sortie, 'w', encoding='utf-8') as f:
                    f.write(code_final)
                
                print(f"✅ Transformation réussie !")
                print(f"• Fichier de sortie : {fichier_sortie}")
                
                # Enregistrement dans l'historique
                self.historique.append({
                    'timestamp': datetime.datetime.now().isoformat(),
                    'source': fichier_source,
                    'sortie': fichier_sortie,
                    'recette': nom_recette,
                    'transformations': stats_transform['transformations']
                })
                
                return True
                
            except Exception as e:
                print(f"X Erreur transformation AST : {e}")
                return False
                
        except Exception as e:
            print(f"X Erreur générale : {e}")
            return False
    
    def _ajouter_imports_et_config(self, code):
        """Ajoute les imports et la configuration logging."""
        imports_logging = "import logging\n"
        config_logging = """
# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
"""
        
        # Insérer après les imports existants ou au début
        lignes = code.split('\n')
        position_insertion = 0
        
        # Trouver la fin des imports
        for i, ligne in enumerate(lignes):
            if ligne.strip().startswith(('import ', 'from ')):
                position_insertion = i + 1
            elif ligne.strip() and not ligne.strip().startswith('#'):
                break
        
        # Vérifier si logging est déjà importé
        if not any('import logging' in ligne for ligne in lignes[:position_insertion]):
            lignes.insert(position_insertion, imports_logging.strip())
            lignes.insert(position_insertion + 1, config_logging.strip())
        
        return '\n'.join(lignes)
    
    def _ajouter_entete(self, code, fichier_source, recette):
        """Ajoute un en-tête informatif au fichier transformé."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entete = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
FICHIER TRANSFORMÉ PAR OUTIL AST
==============================================================================

Fichier original : {os.path.basename(fichier_source)}
Recette appliquée : {recette}
Date transformation : {timestamp}
Outil : Refonte AST v2.4

Modifications principales :
- Conversion print() vers logging.info()
- Ajout configuration logging
- Préservation de la structure originale
==============================================================================
"""

'''
        return entete + code
    
    def demarrer_session_interactive(self, fichier_source=None):
        """Démarre une session interactive pour créer des recettes personnalisées."""
        self.session_active = True
        
        print("*** SESSION INTERACTIVE - CRÉATION DE RECETTES ***")
        print("=" * 55)
        
        if not fichier_source:
            fichier_source = browser_fichier_interactif()
            if not fichier_source:
                print("Aucun fichier sélectionné. Session annulée.")
                return
        
        while self.session_active:
            print(f"\n*** FICHIER ACTUEL : {os.path.basename(fichier_source)} ***")
            print("=" * 50)
            print("1. Analyser le fichier")
            print("2. Appliquer une recette existante")
            print("3. Créer une recette personnalisée")
            print("4. Voir l'historique des transformations")
            print("5. Changer de fichier")
            print("6. Quitter la session")
            
            choix = input("Votre choix (1-6): ").strip()
            
            if choix == "1":
                self._analyser_fichier_interactif(fichier_source)
            elif choix == "2":
                self._appliquer_recette_interactive(fichier_source)
            elif choix == "3":
                self._creer_recette_personnalisee(fichier_source)
            elif choix == "4":
                self._afficher_historique()
            elif choix == "5":
                nouveau_fichier = browser_fichier_interactif()
                if nouveau_fichier:
                    fichier_source = nouveau_fichier
            elif choix == "6":
                self.session_active = False
                print("Session terminée.")
            else:
                print("Choix invalide.")
    
    def _analyser_fichier_interactif(self, fichier_source):
        """Analyse interactive d'un fichier."""
        print(f"\n*** ANALYSE : {os.path.basename(fichier_source)} ***")
        print("=" * 40)
        
        if self.analyseur.analyser_fichier(fichier_source):
            rapport = self.analyseur.obtenir_rapport()
            
            print(f"• Fonctions : {rapport['fonctions']}")
            print(f"• Classes : {rapport['classes']}")
            print(f"• Imports : {rapport['imports']}")
            print(f"• Appels print() : {rapport['print_calls']}")
            
            if rapport['print_calls'] > 0:
                print(f"• Lignes avec print() : {rapport.get('print_lines', 'N/A')}")
            
            if self.analyseur.erreurs:
                print("• Erreurs détectées :")
                for erreur in self.analyseur.erreurs:
                    print(f"  - {erreur}")
        else:
            print("Erreur lors de l'analyse du fichier.")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    def _appliquer_recette_interactive(self, fichier_source):
        """Application interactive d'une recette."""
        print("\n*** RECETTES DISPONIBLES ***")
        print("=" * 30)
        
        recettes = self.gestionnaire_recettes.lister_recettes()
        for i, nom_recette in enumerate(recettes, 1):
            recette = self.gestionnaire_recettes.obtenir_recette(nom_recette)
            print(f"{i}. {recette.get('nom', nom_recette)}")
            print(f"   {recette.get('description', 'Aucune description')}")
        
        try:
            choix_recette = int(input(f"Choisissez une recette (1-{len(recettes)}): ")) - 1
            if 0 <= choix_recette < len(recettes):
                nom_recette = recettes[choix_recette]
                
                # Génération du nom de fichier de sortie
                base, ext = os.path.splitext(fichier_source)
                fichier_sortie = f"{base}_{nom_recette}{ext}"
                
                self.appliquer_recette(fichier_source, fichier_sortie, nom_recette)
                
                input("\nAppuyez sur Entrée pour continuer...")
            else:
                print("Choix invalide.")
        except ValueError:
            print("Choix invalide.")
    
    def _creer_recette_personnalisee(self, fichier_source):
        """Création interactive d'une recette personnalisée."""
        print("\n*** CRÉATION DE RECETTE PERSONNALISÉE ***")
        print("=" * 40)
        print("Cette fonctionnalité sera implémentée dans une version future.")
        print("Pour l'instant, utilisez les recettes existantes.")
        input("\nAppuyez sur Entrée pour continuer...")
    
    def _afficher_historique(self):
        """Affiche l'historique des transformations."""
        print("\n*** HISTORIQUE DES TRANSFORMATIONS ***")
        print("=" * 40)
        
        if not self.historique:
            print("Aucune transformation effectuée dans cette session.")
        else:
            for i, entree in enumerate(self.historique, 1):
                print(f"{i}. {entree['timestamp']}")
                print(f"   Source : {os.path.basename(entree['source'])}")
                print(f"   Sortie : {os.path.basename(entree['sortie'])}")
                print(f"   Recette : {entree['recette']}")
                print()
        
        input("Appuyez sur Entrée pour continuer...")

# ==============================================================================
# BROWSER DE FICHIERS INTERACTIF
# ==============================================================================

def browser_fichier_interactif():
    """Browser interactif pour sélectionner un fichier Python."""
    
    print("*** SÉLECTION DE FICHIER PYTHON ***")
    print("=" * 35)
    
    repertoire_actuel = os.getcwd()
    
    while True:
        print(f"\nRépertoire actuel : {repertoire_actuel}")
        print("-" * 40)
        
        try:
            # Lister les éléments du répertoire
            elements = []
            
            # Ajouter le dossier parent si pas à la racine
            if repertoire_actuel != os.path.dirname(repertoire_actuel):
                elements.append(("📁 ..", "parent"))
            
            # Lister les dossiers
            for item in sorted(os.listdir(repertoire_actuel)):
                chemin_complet = os.path.join(repertoire_actuel, item)
                if os.path.isdir(chemin_complet) and not item.startswith('.'):
                    elements.append((f"📁 {item}/", "dossier", chemin_complet))
            
            # Lister les fichiers Python
            fichiers_python = []
            for item in sorted(os.listdir(repertoire_actuel)):
                if item.endswith('.py') and os.path.isfile(os.path.join(repertoire_actuel, item)):
                    chemin_complet = os.path.join(repertoire_actuel, item)
                    taille = os.path.getsize(chemin_complet)
                    fichiers_python.append((f"🐍 {item} ({format_taille(taille)})", "fichier", chemin_complet))
            
            elements.extend(fichiers_python)
            
            if not elements:
                print("Aucun dossier ou fichier Python trouvé.")
                choix = input("Retour au dossier parent ? (o/N): ").strip().lower()
                if choix in ['o', 'oui']:
                    repertoire_actuel = os.path.dirname(repertoire_actuel)
                else:
                    return None
                continue
            
            # Affichage du menu
            for i, element in enumerate(elements, 1):
                print(f"{i:2d}. {element[0]}")
            
            print(f"\n{len(elements) + 1:2d}. 🔍 Entrer un chemin manuellement")
            print(f"{len(elements) + 2:2d}. ❌ Annuler")
            
            choix = input(f"\nVotre choix (1-{len(elements) + 2}): ").strip()
            
            try:
                index = int(choix) - 1
                
                if index == len(elements):  # Chemin manuel
                    chemin_manuel = input("Entrez le chemin vers le fichier Python : ").strip()
                    if os.path.exists(chemin_manuel) and chemin_manuel.endswith('.py'):
                        return chemin_manuel
                    else:
                        print("Fichier non trouvé ou non valide.")
                        continue
                
                elif index == len(elements) + 1:  # Annuler
                    return None
                
                elif 0 <= index < len(elements):
                    element = elements[index]
                    
                    if element[1] == "parent":
                        repertoire_actuel = os.path.dirname(repertoire_actuel)
                    elif element[1] == "dossier":
                        repertoire_actuel = element[2]
                    elif element[1] == "fichier":
                        return element[2]
                else:
                    print("Choix invalide.")
            
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        except PermissionError:
            print("Accès refusé à ce répertoire.")
            repertoire_actuel = os.path.dirname(repertoire_actuel)
        except Exception as e:
            print(f"Erreur : {e}")
            return None

def launch_file_selector_with_fallback():
    """Lance le sélecteur GUI avec fallback vers le browser existant."""
    
    print("DEBUG: Appel de launch_file_selector_with_fallback...")
    
    try:
        from composants_browser.file_selector_ui import launch_file_selector_integrated
        print("DEBUG: Importation de la GUI réussie.")
        
        fichiers_python = launch_file_selector_integrated()
        print(f"DEBUG: La GUI a retourné : {fichiers_python}")
        
        if fichiers_python:
            print(f"+ Interface GUI : {len(fichiers_python)} fichier(s) sélectionné(s)")
            return fichiers_python
        else:
            print("! Aucune sélection GUI, retour au browser texte...")
            fichier_unique = browser_fichier_interactif()
            return [fichier_unique] if fichier_unique else []
        
    except Exception as e:
        print(f"DEBUG: ERREUR CAPTURÉE DANS LE FALLBACK : {e}")
        print(f"! Interface GUI non disponible ({e}), utilisation du browser texte...")
        fichier_unique = browser_fichier_interactif()
        return [fichier_unique] if fichier_unique else []

# ==============================================================================
# FONCTIONS DE DÉMONSTRATION PRINCIPALES
# ==============================================================================

def demo():
    """Démonstration avec sélection de fichiers ou dossiers multiples."""
    global COLAB_ENV, VSCODE_ENV
    
    print("*** DÉMONSTRATION - Outil de Refonte AST ***")
    print("=" * 50)
    
    env_info = []
    if COLAB_ENV:
        env_info.append("*** Google Colab ***")
    if VSCODE_ENV:
        env_info.append("*** VSCode/Jupyter ***")
    if not env_info:
        env_info.append("*** Terminal ***")
    
    print("Environnement détecté : " + ' + '.join(env_info))
    print("Fonctionnalités disponibles : Interface GUI, Browser interactif, Traitement lot\n")
    
    print("*** SÉLECTION DES FICHIERS À TRANSFORMER ***")
    print("=" * 45)
    
    # Lancer la sélection (GUI ou fallback)
    fichiers_cibles = launch_file_selector_with_fallback()
    
    if not fichiers_cibles:
        print("X Aucun fichier sélectionné. Démonstration annulée.")
        input("Appuyez sur Entrée pour revenir au menu principal...")
        return
    
    # Filtrer les fichiers valides
    fichiers_valides = []
    for fichier in fichiers_cibles:
        if fichier and os.path.exists(fichier) and fichier.endswith('.py'):
            fichiers_valides.append(fichier)
        elif fichier:
            print(f"! Fichier ignoré (non valide) : {fichier}")
    
    fichiers_cibles = fichiers_valides
    
    if not fichiers_cibles:
        print("X Aucun fichier Python valide trouvé.")
        input("Appuyez sur Entrée pour revenir au menu principal...")
        return
    
    # Affichage des statistiques
    print(f"*** FICHIERS SÉLECTIONNÉS : {len(fichiers_cibles)} ***")
    print("=" * 50)
    
    if len(fichiers_cibles) == 1:
        # Mode fichier unique
        fichier = fichiers_cibles[0]
        try:
            taille = format_taille(os.path.getsize(fichier))
            print(f"• Fichier : {os.path.basename(fichier)}")
            print(f"• Chemin : {os.path.dirname(fichier)}")
            print(f"• Taille : {taille}")
            
            # Analyse rapide du fichier
            try:
                analyseur = AnalyseurCode()
                with open(fichier, 'r', encoding='utf-8') as f:
                    code_contenu = f.read()
                
                fonctions = analyseur.extraire_fonctions(code_contenu)
                classes = analyseur.extraire_classes(code_contenu)
                stats = analyseur.compter_lignes_par_type(code_contenu)
                
                print(f"• Lignes de code : {stats['code']}")
                print(f"• Fonctions : {len(fonctions)}")
                print(f"• Classes : {len(classes)}")
                
                if fonctions:
                    noms_fonctions = [f['nom'] for f in fonctions[:3]]
                    print(f"• Fonctions principales : {', '.join(noms_fonctions)}")
                    if len(fonctions) > 3:
                        print(f"  ... et {len(fonctions) - 3} autres")
                        
            except Exception as e:
                print(f"! Erreur d'analyse : {e}")
                
        except Exception as e:
            print(f"• Fichier : {os.path.basename(fichier)} (erreur : {e})")
    
    else:
        # Mode lot
        taille_totale = sum(os.path.getsize(f) for f in fichiers_cibles if os.path.exists(f))
        dossiers_uniques = set(os.path.dirname(f) for f in fichiers_cibles)
        
        print(f"• Nombre total : {len(fichiers_cibles)} fichiers Python")
        print(f"• Taille totale : {format_taille(taille_totale)}")
        print(f"• Dossiers sources : {len(dossiers_uniques)}")
        
        print(f"\nÉchantillon :")
        for i, fichier in enumerate(fichiers_cibles[:3], 1):
            nom_court = os.path.basename(fichier)
            dossier_parent = os.path.basename(os.path.dirname(fichier))
            print(f"  {i}. {nom_court} (dans {dossier_parent})")
        
        if len(fichiers_cibles) > 3:
            print(f"  ... et {len(fichiers_cibles) - 3} autres fichiers")
    
    # Suggestions de transformations
    print("\n*** TRANSFORMATIONS QUI SERONT APPLIQUÉES ***")
    suggestions = [
        "✓ Ajout d'en-tête avec informations de transformation",
        "✓ Import du module logging en début de fichier",
        "✓ Configuration du logging (niveau INFO)",
        "✓ Remplacement des print() par logging.info()",
        "✓ Préservation de la structure et logique originales"
    ]
    
    for suggestion in suggestions:
        print(suggestion)
    
    # Confirmation
    if len(fichiers_cibles) == 1:
        message = f"Confirmer la transformation du fichier '{os.path.basename(fichiers_cibles[0])}' ?"
    else:
        message = f"Confirmer la transformation des {len(fichiers_cibles)} fichiers sélectionnés ?"
    
    print(f"\n*** {message}")
    confirmation = input("Confirmer ? (o/N) : ").strip().lower()
    
    if confirmation not in ['o', 'oui', 'y', 'yes']:
        print("X Démonstration annulée")
        input("Appuyez sur Entrée pour revenir au menu principal...")
        return
    
    # Traitement
    print("*** LANCEMENT DE LA TRANSFORMATION ***")
    print("=" * 40)
    
    orchestrateur = OrchestrateurAST(mode_colab=True)
    
    try:
        if len(fichiers_cibles) == 1:
            # Traitement fichier unique
            fichier_source = fichiers_cibles[0]
            base, ext = os.path.splitext(fichier_source)
            fichier_sortie = base + "_transforme" + ext
            
            print(f"Transformation : {os.path.basename(fichier_source)} -> {os.path.basename(fichier_sortie)}")
            
            success = orchestrateur.appliquer_recette(fichier_source, fichier_sortie)
            
            if success:
                print("*** TRANSFORMATION RÉUSSIE ! ***")
                print("=" * 30)
                print(f"+ Fichier original : {fichier_source}")
                print(f"+ Fichier transformé : {fichier_sortie}")
                
                # Gestion environnement spécifique
                gerer_sortie_environnement([fichier_sortie], "unique")
                
                # Proposer l'aperçu des différences
                voir_diff = input("\n*** Voir les différences ? (o/N) : ").strip().lower()
                if voir_diff in ['o', 'oui', 'y', 'yes']:
                    afficher_diff_simple(fichier_source, fichier_sortie)
            
            else:
                print("X La transformation a échoué")
        
        else:
            # Traitement en lot (version simplifiée)
            print(f"Mode traitement en lot : {len(fichiers_cibles)} fichiers")
            
            # Créer dossier de sortie
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dossier_sortie = f"transformations_batch_{timestamp}"
            os.makedirs(dossier_sortie, exist_ok=True)
            
            print(f"Dossier de sortie : {dossier_sortie}")
            print("-" * 40)
            
            reussis = 0
            echecs = 0
            
            for i, fichier_source in enumerate(fichiers_cibles, 1):
                print(f"[{i}/{len(fichiers_cibles)}] {os.path.basename(fichier_source)}")
                
                try:
                    nom_base = os.path.splitext(os.path.basename(fichier_source))[0]
                    fichier_sortie = os.path.join(dossier_sortie, f"{nom_base}_transforme.py")
                    
                    if orchestrateur.appliquer_recette(fichier_source, fichier_sortie):
                        reussis += 1
                        print(f"  ✅ Réussi")
                    else:
                        echecs += 1
                        print(f"  ❌ Échec")
                except Exception as e:
                    echecs += 1
                    print(f"  ❌ Erreur : {e}")
            
            print("=" * 40)
            print(f"*** TRAITEMENT LOT TERMINÉ ***")
            print(f"Succès : {reussis}/{len(fichiers_cibles)}")
            print(f"Échecs : {echecs}")
            print(f"Taux de réussite : {(reussis/len(fichiers_cibles)*100):.1f}%")
            print(f"Dossier : {dossier_sortie}")
            
            if reussis > 0:
                gerer_sortie_environnement(None, "lot", dossier_sortie)
    
    except Exception as e:
        print(f"X Erreur : {e}")
        print("! Vérifiez que les fichiers sont accessibles et contiennent du Python valide.")
    
    print("\n*** DÉMONSTRATION TERMINÉE ***")
    input("Appuyez sur Entrée pour revenir au menu principal...")

def gerer_sortie_environnement(fichiers_sortie, mode_traitement, dossier_sortie=None):
    """Gère la sortie selon l'environnement (Colab, VSCode, Terminal)."""
    global COLAB_ENV, VSCODE_ENV
    
    if COLAB_ENV:
        print("*** OPTIONS GOOGLE COLAB ***")
        print("=" * 25)
        
        if mode_traitement == "unique" and fichiers_sortie:
            fichier = fichiers_sortie[0]
            telecharger = input(f"Télécharger '{os.path.basename(fichier)}' ? (o/N) : ").strip().lower()
            if telecharger in ['o', 'oui', 'y', 'yes']:
                try:
                    files.download(fichier)
                    print(f"+ Téléchargement de '{fichier}' lancé !")
                except Exception as e:
                    print(f"X Erreur de téléchargement : {e}")
        
        elif mode_traitement == "lot":
            print("Pour le traitement en lot, les fichiers sont disponibles dans le dossier de sortie.")
            creer_zip = input("Créer une archive ZIP pour téléchargement ? (o/N) : ").strip().lower()
            if creer_zip in ['o', 'oui', 'y', 'yes']:
                try:
                    import zipfile
                    nom_zip = f"{dossier_sortie}.zip"
                    
                    with zipfile.ZipFile(nom_zip, 'w') as zipf:
                        for root, dirs, files in os.walk(dossier_sortie):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, '.')
                                zipf.write(file_path, arcname)
                    
                    files.download(nom_zip)
                    print(f"+ Archive '{nom_zip}' créée et téléchargement lancé !")
                        
                except Exception as e:
                    print(f"X Erreur création archive : {e}")
    
    elif VSCODE_ENV:
        print("*** ENVIRONNEMENT VSCODE/JUPYTER ***")
        print("=" * 30)
        print("Les fichiers transformés sont disponibles dans votre workspace :")
        
        if mode_traitement == "unique" and fichiers_sortie:
            print(f"• {os.path.abspath(fichiers_sortie[0])}")
        else:
            print(f"• Consultez le dossier '{dossier_sortie or 'transformations_batch_[timestamp]'}'")
    
    else:
        print("*** ENVIRONNEMENT TERMINAL ***")
        print("=" * 25)
        
        if mode_traitement == "unique" and fichiers_sortie:
            print(f"• Fichier transformé : {os.path.abspath(fichiers_sortie[0])}")
        else:
            print(f"• Consultez le dossier de sortie : {dossier_sortie}")
            
        ouvrir_dossier = input("Ouvrir le dossier contenant les fichiers ? (o/N) : ").strip().lower()
        if ouvrir_dossier in ['o', 'oui', 'y', 'yes']:
            try:
                if mode_traitement == "unique" and fichiers_sortie:
                    dossier = os.path.dirname(fichiers_sortie[0])
                else:
                    dossier = dossier_sortie or '.'
                
                import subprocess
                import platform
                
                system = platform.system()
                if system == "Windows":
                    subprocess.run(["explorer", dossier])
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", dossier])
                else:  # Linux
                    subprocess.run(["xdg-open", dossier])
                    
                print(f"+ Dossier ouvert : {dossier}")
                
            except Exception as e:
                print(f"! Impossible d'ouvrir le dossier automatiquement : {e}")
                print(f"  Naviguez manuellement vers : {os.path.abspath(dossier)}")

# ==============================================================================
# MENU PRINCIPAL ET NAVIGATION
# ==============================================================================

def menu_principal():
    """Affiche le menu principal avec les options de démonstration."""
    print("*** OUTIL DE REFONTE AST - VERSION 2.4 ***")
    print("=" * 50)
    print("Bienvenue dans l'outil de transformation de code Python par AST !")
    print("")
    print("*** MODES DISPONIBLES :")
    print("=" * 25)
    print("1. Démonstration")
    print("   > Interface GUI + traitement fichier unique ou lot")
    print("   > Browser interactif avec fallback automatique")
    print("")
    print("2. Démonstration AI")
    print("   > Transformations pilotées par fichier JSON AI")
    print("   > Support des instructions AI complexes")
    print("")
    print("3. Mode Session Interactive")
    print("   > Création de recettes personnalisées")
    print("   > Contrôle total des transformations")
    print("")
    print("4. Quitter")
    print("=" * 50)
    
    try:
        choix = input("Votre choix (1-4): ").strip()
        return choix
    except KeyboardInterrupt:
        print("\nAu revoir !")
        return "4"

def main():
    """Point d'entrée principal du programme."""
    # Mode ligne de commande avec fichier spécifique
    if len(sys.argv) > 1:
        fichier_source = sys.argv[1]
        if os.path.exists(fichier_source):
            print("*** MODE LIGNE DE COMMANDE ***")
            print("Fichier: " + fichier_source)
            orchestrateur = OrchestrateurAST()
            orchestrateur.demarrer_session_interactive(fichier_source)
        else:
            print("X Fichier non trouve: " + fichier_source)
        return
    
    # Lancement direct de l'interface GUI
    print("🚀 Lancement de l'interface graphique...")
    
    try:
        from composants_browser.interface_gui_principale import InterfaceAST
        print("✅ Interface GUI chargée avec succès")
        
        app = InterfaceAST()
        app.run()
        
    except ImportError as e:
        print(f"❌ Interface GUI non disponible : {e}")
        print("📋 Fallback vers le menu texte...")
        
        # Fallback vers l'interface texte
        while True:
            choix = menu_principal()
            
            if choix == "1":
                print("*** LANCEMENT : DÉMONSTRATION ***")
                print("=" * 40)
                demo()
                
            elif choix == "2":
                print("*** LANCEMENT : DÉMONSTRATION AI ***")
                print("=" * 40)
                try:
                    from composants_browser.json_ai_processor import demo_json_ai
                    demo_json_ai()
                except ImportError:
                    print("X Module JSON AI non disponible")
                    print("Assurez-vous que json_ai_processor.py est dans composants_browser/")
                    input("Appuyez sur Entrée pour continuer...")
                except Exception as e:
                    print(f"X Erreur démonstration AI : {e}")
                    input("Appuyez sur Entrée pour continuer...")
                
            elif choix == "3":
                print("*** MODE SESSION INTERACTIVE ***")
                print("=" * 35)
                print("Ce mode vous permet de créer des recettes personnalisées.")
                
                utiliser_fichier = input("Avez-vous un fichier spécifique à transformer ? (o/N): ").strip().lower()
                
                if utiliser_fichier in ['o', 'oui', 'y', 'yes']:
                    fichier_source = browser_fichier_interactif()
                    if fichier_source:
                        orchestrateur = OrchestrateurAST()
                        orchestrateur.demarrer_session_interactive(fichier_source)
                else:
                    orchestrateur = OrchestrateurAST()
                    orchestrateur.demarrer_session_interactive()
                    
            elif choix == "4":
                print("Merci d'avoir utilisé l'Outil de Refonte AST !")
                print("Au revoir ! 👋")
                break
                
            else:
                print("X Choix invalide. Veuillez choisir entre 1 et 4.")
                input("Appuyez sur Entrée pour continuer...")
    
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        print("📋 Fallback vers le menu texte...")
        # Ici aussi on pourrait ajouter le fallback menu texte

# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================

if __name__ == "__main__":
    main()