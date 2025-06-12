#!/usr/bin/env python3
"""
Outil de Refonte de Code par AST - Version Google Colab
=======================================================

Un framework extensible pour la modification automatique de code Python
via l'analyse et la transformation d'arbres syntaxiques abstraits (AST).

Architecture en 3 blocs :
1. Interface Interactive (Le Cerveau)
2. Moteur de Transformation (Le Bras Robotique)
3. Orchestrateur (Le Chef d'Orchestre)
"""

import ast
import json
import os
from typing import List, Dict, Any, Union, Optional
from dataclasses import dataclass, asdict
import textwrap

# ===============================================
# BLOC 1: INTERFACE INTERACTIVE (LE CERVEAU)
# ===============================================

@dataclass
class Instruction:
    """Représente une instruction de transformation."""
    type: str  # 'substitution', 'ajout', 'suppression'
    cible: Any = None
    remplacement: Any = None
    position: str = None  # 'debut', 'fin', 'avant', 'apres'
    contexte: str = None  # nom de fonction, classe, etc.

class InterfaceInteractive:
    """Gère l'interaction avec l'utilisateur pour créer des recettes de transformation."""
    
    def __init__(self, mode_colab=True):
        self.mode_colab = mode_colab
        self.recette = []
    
    def saisir_nombre(self, prompt: str, min_val: int = 0, max_val: int = 100) -> int:
        """Saisie sécurisée d'un nombre avec validation."""
        while True:
            try:
                if self.mode_colab:
                    # En mode Colab, on peut utiliser des widgets pour une meilleure UX
                    print(f"📝 {prompt}")
                
                valeur = input(f"{prompt} ({min_val}-{max_val}): ").strip()
                nombre = int(valeur)
                
                if min_val <= nombre <= max_val:
                    return nombre
                else:
                    print(f"❌ Veuillez entrer un nombre entre {min_val} et {max_val}")
                    
            except ValueError:
                print("❌ Veuillez entrer un nombre valide")
    
    def detecter_type_valeur(self, valeur: str) -> Any:
        """Détecte intelligemment le type de la valeur saisie."""
        valeur = valeur.strip()
        
        # Nombre entier
        try:
            return int(valeur)
        except ValueError:
            pass
        
        # Nombre flottant
        try:
            return float(valeur)
        except ValueError:
            pass
        
        # Booléen
        if valeur.lower() in ['true', 'false']:
            return valeur.lower() == 'true'
        
        # String (enlever les guillemets si présents)
        if valeur.startswith('"') and valeur.endswith('"'):
            return valeur[1:-1]
        if valeur.startswith("'") and valeur.endswith("'"):
            return valeur[1:-1]
        
        # Par défaut, c'est une string
        return valeur
    
    def creer_substitution(self) -> Instruction:
        """Crée une instruction de substitution."""
        print("\n🔄 CRÉATION D'UNE SUBSTITUTION")
        print("Vous pouvez remplacer des valeurs, des noms de variables, etc.")
        
        cible_str = input("Quelle valeur voulez-vous remplacer ? : ")
        cible = self.detecter_type_valeur(cible_str)
        
        remplacement_str = input("Par quelle valeur la remplacer ? : ")
        remplacement = self.detecter_type_valeur(remplacement_str)
        
        contexte = input("Dans quel contexte ? (fonction/classe/global ou ENTER pour global) : ").strip()
        if not contexte:
            contexte = "global"
        
        return Instruction(
            type="substitution",
            cible=cible,
            remplacement=remplacement,
            contexte=contexte
        )
    
    def creer_ajout(self) -> Instruction:
        """Crée une instruction d'ajout de code."""
        print("\n➕ CRÉATION D'UN AJOUT")
        print("Vous pouvez ajouter du code au début/fin de fonctions, etc.")
        
        code_a_ajouter = input("Quel code voulez-vous ajouter ? : ")
        
        print("Où voulez-vous l'ajouter ?")
        print("1. Au début d'une fonction")
        print("2. À la fin d'une fonction")
        print("3. Au début du fichier")
        print("4. À la fin du fichier")
        
        choix = self.saisir_nombre("Votre choix", 1, 4)
        
        positions = {1: "debut", 2: "fin", 3: "debut", 4: "fin"}
        position = positions[choix]
        
        contexte = "global"
        if choix in [1, 2]:
            contexte = input("Dans quelle fonction ? : ").strip()
        
        return Instruction(
            type="ajout",
            remplacement=code_a_ajouter,
            position=position,
            contexte=contexte
        )
    
    def creer_recette_interactive(self) -> List[Instruction]:
        """Interface principale pour créer une recette complète."""
        print("🧪 CRÉATEUR DE RECETTE DE TRANSFORMATION AST")
        print("=" * 50)
        
        # Substitutions
        nb_substitutions = self.saisir_nombre("Combien de substitutions voulez-vous faire ?", 0, 20)
        
        for i in range(nb_substitutions):
            print(f"\n--- Substitution {i+1}/{nb_substitutions} ---")
            instruction = self.creer_substitution()
            self.recette.append(instruction)
        
        # Ajouts
        nb_ajouts = self.saisir_nombre("Combien d'ajouts de code voulez-vous faire ?", 0, 10)
        
        for i in range(nb_ajouts):
            print(f"\n--- Ajout {i+1}/{nb_ajouts} ---")
            instruction = self.creer_ajout()
            self.recette.append(instruction)
        
        return self.recette
    
    def afficher_recette(self, recette: List[Instruction]) -> None:
        """Affiche la recette de manière lisible."""
        print("\n📋 RÉCAPITULATIF DE VOTRE RECETTE")
        print("=" * 40)
        
        if not recette:
            print("Aucune instruction dans la recette.")
            return
        
        for i, instruction in enumerate(recette, 1):
            print(f"\n{i}. {instruction.type.upper()}")
            
            if instruction.type == "substitution":
                print(f"   Remplacer: {instruction.cible}")
                print(f"   Par: {instruction.remplacement}")
                print(f"   Contexte: {instruction.contexte}")
            
            elif instruction.type == "ajout":
                print(f"   Code: {instruction.remplacement}")
                print(f"   Position: {instruction.position}")
                print(f"   Contexte: {instruction.contexte}")

# ===============================================
# BLOC 2: MOTEUR DE TRANSFORMATION (LE BRAS ROBOTIQUE)
# ===============================================

class TransformateurPolyvalent(ast.NodeTransformer):
    """
    Transformateur AST qui applique une recette d'instructions.
    Hérite de ast.NodeTransformer pour parcourir et modifier l'AST.
    """
    
    def __init__(self, recette: List[Instruction]):
        self.recette = recette
        self.contexte_actuel = "global"
        self.modifications_appliquees = []
    
    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """Visite les constantes (nombres, strings, etc.)."""
        for instruction in self.recette:
            if (instruction.type == "substitution" and 
                instruction.cible == node.value and
                (instruction.contexte == "global" or instruction.contexte == self.contexte_actuel)):
                
                self.modifications_appliquees.append(f"Remplacé {node.value} par {instruction.remplacement}")
                node.value = instruction.remplacement
                break
        
        return node
    
    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Visite les noms de variables."""
        for instruction in self.recette:
            if (instruction.type == "substitution" and 
                instruction.cible == node.id and
                (instruction.contexte == "global" or instruction.contexte == self.contexte_actuel)):
                
                self.modifications_appliquees.append(f"Renommé variable {node.id} en {instruction.remplacement}")
                node.id = instruction.remplacement
                break
        
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visite les définitions de fonctions."""
        ancien_contexte = self.contexte_actuel
        self.contexte_actuel = node.name
        
        # Chercher les ajouts pour cette fonction
        for instruction in self.recette:
            if (instruction.type == "ajout" and 
                instruction.contexte == node.name):
                
                try:
                    # Parser le code à ajouter
                    code_ast = ast.parse(instruction.remplacement)
                    nouvelles_instructions = code_ast.body
                    
                    if instruction.position == "debut":
                        node.body = nouvelles_instructions + node.body
                        self.modifications_appliquees.append(f"Ajouté code au début de {node.name}")
                    elif instruction.position == "fin":
                        node.body = node.body + nouvelles_instructions
                        self.modifications_appliquees.append(f"Ajouté code à la fin de {node.name}")
                        
                except SyntaxError as e:
                    print(f"⚠️ Erreur de syntaxe dans le code à ajouter: {e}")
        
        # Continuer la visite des enfants
        self.generic_visit(node)
        
        self.contexte_actuel = ancien_contexte
        return node

# ===============================================
# BLOC 3: ORCHESTRATEUR (LE CHEF D'ORCHESTRE)
# ===============================================

class OrchestrateurAST:
    """Coordonne l'ensemble du processus de transformation."""
    
    def __init__(self, mode_colab=True):
        self.mode_colab = mode_colab
        self.interface = InterfaceInteractive(mode_colab)
    
    def lire_fichier_source(self, chemin: str) -> str:
        """Lit le fichier source à modifier."""
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {chemin}")
            return None
        except Exception as e:
            print(f"❌ Erreur de lecture: {e}")
            return None
    
    def ecrire_fichier_resultat(self, code: str, chemin: str) -> bool:
        """Écrit le code modifié dans un fichier."""
        try:
            with open(chemin, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ Fichier sauvegardé: {chemin}")
            return True
        except Exception as e:
            print(f"❌ Erreur d'écriture: {e}")
            return False
    
    def sauvegarder_recette(self, recette: List[Instruction], chemin: str) -> None:
        """Sauvegarde la recette au format JSON pour réutilisation."""
        try:
            recette_dict = [asdict(instruction) for instruction in recette]
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(recette_dict, f, indent=2, ensure_ascii=False)
            print(f"📝 Recette sauvegardée: {chemin}")
        except Exception as e:
            print(f"⚠️ Erreur de sauvegarde de recette: {e}")
    
    def charger_recette(self, chemin: str) -> List[Instruction]:
        """Charge une recette depuis un fichier JSON."""
        try:
            with open(chemin, 'r', encoding='utf-8') as f:
                recette_dict = json.load(f)
            return [Instruction(**inst) for inst in recette_dict]
        except Exception as e:
            print(f"⚠️ Erreur de chargement de recette: {e}")
            return []
    
    def appliquer_recette(self, fichier_source: str, fichier_destination: str = None) -> bool:
        """Applique une recette de transformation sur un fichier."""
        
        # 1. Créer ou charger la recette
        print("Voulez-vous :")
        print("1. Créer une nouvelle recette")
        print("2. Charger une recette existante")
        
        choix = input("Votre choix (1 ou 2) : ").strip()
        
        if choix == "2":
            chemin_recette = input("Chemin vers la recette JSON : ").strip()
            recette = self.charger_recette(chemin_recette)
            if not recette:
                print("❌ Impossible de charger la recette, création d'une nouvelle...")
                recette = self.interface.creer_recette_interactive()
        else:
            recette = self.interface.creer_recette_interactive()
        
        if not recette:
            print("❌ Aucune instruction dans la recette.")
            return False
        
        # 2. Afficher et confirmer la recette
        self.interface.afficher_recette(recette)
        
        confirmation = input("\n🤔 Voulez-vous appliquer cette recette ? (o/N) : ").strip().lower()
        if confirmation not in ['o', 'oui', 'y', 'yes']:
            print("❌ Opération annulée.")
            return False
        
        # 3. Sauvegarder la recette
        sauver = input("Voulez-vous sauvegarder cette recette ? (o/N) : ").strip().lower()
        if sauver in ['o', 'oui', 'y', 'yes']:
            nom_recette = input("Nom du fichier recette (sans .json) : ").strip()
            if nom_recette:
                self.sauvegarder_recette(recette, f"{nom_recette}.json")
        
        # 4. Lire le fichier source
        code_source = self.lire_fichier_source(fichier_source)
        if code_source is None:
            return False
        
        # 5. Parser le code en AST
        try:
            arbre_ast = ast.parse(code_source)
        except SyntaxError as e:
            print(f"❌ Erreur de syntaxe dans le fichier source: {e}")
            return False
        
        # 6. Appliquer les transformations
        transformateur = TransformateurPolyvalent(recette)
        arbre_modifie = transformateur.visit(arbre_ast)
        
        # 7. Convertir l'AST modifié en code
        try:
            import astor  # Meilleure préservation de la mise en forme
            code_modifie = astor.to_source(arbre_modifie)
        except ImportError:
            # Fallback vers ast.unparse si astor n'est pas disponible
            try:
                code_modifie = ast.unparse(arbre_modifie)
            except AttributeError:
                print("❌ Python 3.9+ requis pour ast.unparse, ou installez astor")
                return False
        
        # 8. Sauvegarder le résultat
        if fichier_destination is None:
            base, ext = os.path.splitext(fichier_source)
            fichier_destination = f"{base}_modifie{ext}"
        
        success = self.ecrire_fichier_resultat(code_modifie, fichier_destination)
        
        # 9. Afficher le rapport
        if success:
            print("\n📊 RAPPORT DE TRANSFORMATION")
            print("=" * 30)
            if transformateur.modifications_appliquees:
                for modif in transformateur.modifications_appliquees:
                    print(f"✅ {modif}")
            else:
                print("ℹ️ Aucune modification appliquée")
        
        return success

# ===============================================
# INTERFACE COLAB SIMPLIFIÉE
# ===============================================

def demo_colab():
    """Fonction de démonstration pour Google Colab."""
    print("🚀 DEMO - Outil de Refonte AST pour Google Colab")
    print("=" * 50)
    
    # Créer un fichier d'exemple
    code_exemple = '''
def calculer_moyenne(a, b):
    somme = a + b
    resultat = somme / 2
    return resultat

def afficher_resultat():
    x = 10
    y = 20
    moyenne = calculer_moyenne(x, y)
    print("La moyenne est:", moyenne)

if __name__ == "__main__":
    afficher_resultat()
'''
    
    with open("exemple.py", "w") as f:
        f.write(code_exemple)
    
    print("📝 Fichier d'exemple créé: exemple.py")
    print("\nContenu:")
    print(code_exemple)
    
    # Lancer l'orchestrateur
    orchestrateur = OrchestrateurAST(mode_colab=True)
    orchestrateur.appliquer_recette("exemple.py", "exemple_modifie.py")

# ===============================================
# POINT D'ENTRÉE PRINCIPAL
# ===============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Mode ligne de commande
        fichier_source = sys.argv[1]
        fichier_dest = sys.argv[2] if len(sys.argv) > 2 else None
        
        orchestrateur = OrchestrateurAST(mode_colab=False)
        orchestrateur.appliquer_recette(fichier_source, fichier_dest)
    else:
        # Mode démonstration
        demo_colab()
