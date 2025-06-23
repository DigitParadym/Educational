# ===============================================
# ARCHITECTURE POUR CONSOMMATION JSON AI
# ===============================================

# 1. STRUCTURE JSON ATTENDUE DE L'AI

"""
Format JSON que l'AI doit produire :

{
    "version": "1.0",
    "timestamp": "2024-01-15T10:30:00Z",
    "source_analysis": {
        "files_analyzed": ["file1.py", "file2.py"],
        "total_functions": 15,
        "total_classes": 3,
        "complexity_score": 7.2
    },
    "transformations": [
        {
            "id": "transform_1",
            "type": "global_import",
            "description": "Ajouter import logging",
            "priority": 1,
            "instruction": {
                "type": "ajout",
                "contexte": "global",
                "position": "debut",
                "remplacement": "import logging\\nlogging.basicConfig(level=logging.INFO)"
            }
        },
        {
            "id": "transform_2", 
            "type": "function_modification",
            "description": "Remplacer print par logging dans fonction main",
            "priority": 2,
            "target_function": "main",
            "instruction": {
                "type": "substitution",
                "contexte": "main",
                "cible": "print",
                "remplacement": "logging.info"
            }
        },
        {
            "id": "transform_3",
            "type": "conditional_replacement",
            "description": "Ajouter gestion d'erreurs si non présente",
            "priority": 3,
            "condition": "no_error_handling",
            "instruction": {
                "type": "ajout",
                "contexte": "main",
                "position": "fin",
                "remplacement": "except Exception as e:\\n    logging.error(f\\\"Erreur: {e}\\\")"
            }
        }
    ],
    "validation_rules": [
        {
            "rule": "syntax_check",
            "enabled": true
        },
        {
            "rule": "import_check", 
            "enabled": true
        }
    ]
}
"""

# 2. ANALYSEUR JSON AI INTELLIGENT

class AnalyseurJSONAI:
    """Analyseur et validateur pour les fichiers JSON de transformations AI."""
    
    def __init__(self):
        self.schema_version = "1.0"
        self.transformations_supportees = {
            "ajout", "substitution", "suppression", "remplacement_bloc"
        }
    
    def charger_json_ai(self, chemin_json: str):
        """Charge et valide un fichier JSON de transformations AI."""
        try:
            with open(chemin_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validation de base
            if not self.valider_structure(data):
                return None
            
            print(f"+ JSON AI chargé : {len(data.get('transformations', []))} transformations")
            return data
            
        except json.JSONDecodeError as e:
            print(f"X Erreur format JSON : {e}")
            return None
        except FileNotFoundError:
            print(f"X Fichier JSON non trouvé : {chemin_json}")
            return None
        except Exception as e:
            print(f"X Erreur chargement JSON : {e}")
            return None
    
    def valider_structure(self, data):
        """Valide la structure du JSON AI."""
        
        # Champs obligatoires
        champs_requis = ["version", "transformations"]
        for champ in champs_requis:
            if champ not in data:
                print(f"X Champ obligatoire manquant : {champ}")
                return False
        
        # Validation des transformations
        transformations = data.get("transformations", [])
        for i, transform in enumerate(transformations):
            if not self.valider_transformation(transform, i):
                return False
        
        print(f"+ Structure JSON validée : {len(transformations)} transformations")
        return True
    
    def valider_transformation(self, transform, index):
        """Valide une transformation individuelle."""
        
        # Champs obligatoires pour une transformation
        champs_requis = ["type", "instruction"]
        for champ in champs_requis:
            if champ not in transform:
                print(f"X Transformation {index}: champ '{champ}' manquant")
                return False
        
        # Validation de l'instruction
        instruction = transform["instruction"]
        if "type" not in instruction:
            print(f"X Transformation {index}: type d'instruction manquant")
            return False
        
        type_instruction = instruction["type"]
        if type_instruction not in self.transformations_supportees:
            print(f"X Transformation {index}: type '{type_instruction}' non supporté")
            return False
        
        return True
    
    def convertir_vers_instructions(self, data_json):
        """Convertit le JSON AI en instructions compatibles avec le moteur AST."""
        
        instructions = []
        transformations = data_json.get("transformations", [])
        
        # Trier par priorité si disponible
        transformations.sort(key=lambda x: x.get("priority", 999))
        
        for transform in transformations:
            try:
                instruction_data = transform["instruction"]
                
                # Créer l'objet Instruction
                instruction = Instruction(
                    type=instruction_data["type"],
                    cible=instruction_data.get("cible"),
                    remplacement=instruction_data.get("remplacement"),
                    contexte=instruction_data.get("contexte"),
                    position=instruction_data.get("position")
                )
                
                instructions.append({
                    "instruction": instruction,
                    "metadata": {
                        "id": transform.get("id", f"transform_{len(instructions)}"),
                        "description": transform.get("description", ""),
                        "type": transform.get("type", "unknown")
                    }
                })
                
            except Exception as e:
                print(f"! Erreur conversion transformation : {e}")
                continue
        
        print(f"+ {len(instructions)} instructions créées depuis le JSON")
        return instructions

# 3. ORCHESTRATEUR ÉTENDU POUR JSON AI

class OrchestrateurAI(OrchestrateurAST):
    """Orchestrateur étendu pour traiter les instructions JSON de l'AI."""
    
    def __init__(self, mode_colab: bool = False):
        super().__init__(mode_colab)
        self.analyseur_json = AnalyseurJSONAI()
        self.transformations_appliquees = []
    
    def appliquer_json_ai(self, fichiers_source, chemin_json):
        """Applique les transformations JSON AI à une liste de fichiers."""
        
        print("*** APPLICATION JSON AI ***")
        print("=" * 30)
        
        # Charger le JSON AI
        data_json = self.analyseur_json.charger_json_ai(chemin_json)
        if not data_json:
            return False
        
        # Convertir en instructions
        instructions_ai = self.analyseur_json.convertir_vers_instructions(data_json)
        if not instructions_ai:
            print("X Aucune instruction valide trouvée")
            return False
        
        # Afficher le plan de transformation
        self.afficher_plan_transformation(data_json, instructions_ai)
        
        # Traitement selon le nombre de fichiers
        if len(fichiers_source) == 1:
            return self.appliquer_ai_fichier_unique(fichiers_source[0], instructions_ai)
        else:
            return self.appliquer_ai_lot(fichiers_source, instructions_ai)
    
    def afficher_plan_transformation(self, data_json, instructions_ai):
        """Affiche le plan de transformation de l'AI."""
        
        print("*** PLAN DE TRANSFORMATION AI ***")
        print("-" * 35)
        
        # Informations générales
        if "source_analysis" in data_json:
            analysis = data_json["source_analysis"]
            print(f"• Fichiers analysés par AI : {analysis.get('files_analyzed', 'N/A')}")
            print(f"• Fonctions détectées : {analysis.get('total_functions', 'N/A')}")
            print(f"• Classes détectées : {analysis.get('total_classes', 'N/A')}")
            if "complexity_score" in analysis:
                print(f"• Score de complexité : {analysis['complexity_score']}/10")
            print()
        
        # Plan des transformations
        print("Transformations prévues :")
        for i, instr_data in enumerate(instructions_ai, 1):
            metadata = instr_data["metadata"]
            instruction = instr_data["instruction"]
            
            print(f"{i}. {metadata['description']}")
            print(f"   Type: {instruction.type} | Contexte: {instruction.contexte or 'global'}")
            
            if instruction.type == "substitution":
                print(f"   Remplacer '{instruction.cible}' par '{instruction.remplacement}'")
            elif instruction.type == "ajout":
                preview = instruction.remplacement[:40] + "..." if len(instruction.remplacement or "") > 40 else instruction.remplacement
                print(f"   Ajouter: {preview}")
        
        print("-" * 35)
    
    def appliquer_ai_fichier_unique(self, fichier_source, instructions_ai):
        """Applique l'AI à un fichier unique."""
        
        print(f"Application AI : {os.path.basename(fichier_source)}")
        
        try:
            # Charger le code source
            with open(fichier_source, 'r', encoding='utf-8') as f:
                code_source = f.read()
            
            if not self.moteur.charger_code(code_source):
                return False
            
            # Appliquer chaque instruction
            transformations_reussies = 0
            for i, instr_data in enumerate(instructions_ai, 1):
                instruction = instr_data["instruction"]
                metadata = instr_data["metadata"]
                
                print(f"  Étape {i}: {metadata['description']}")
                
                if self.moteur.appliquer_instruction(instruction):
                    transformations_reussies += 1
                    self.transformations_appliquees.append(metadata)
                else:
                    print(f"    ! Échec étape {i}")
            
            # Générer le code modifié
            code_modifie = self.moteur.generer_code_modifie()
            if not code_modifie:
                print("X Impossible de générer le code modifié")
                return False
            
            # Sauvegarder
            nom_base, extension = os.path.splitext(fichier_source)
            fichier_sortie = nom_base + "_ai_transforme" + extension
            
            with open(fichier_sortie, 'w', encoding='utf-8') as f:
                f.write(code_modifie)
            
            print(f"+ Transformation AI réussie !")
            print(f"  Transformations appliquées : {transformations_reussies}/{len(instructions_ai)}")
            print(f"  Fichier de sortie : {fichier_sortie}")
            
            return True
            
        except Exception as e:
            print(f"X Erreur transformation AI : {e}")
            return False
    
    def appliquer_ai_lot(self, fichiers_source, instructions_ai):
        """Applique l'AI à un lot de fichiers."""
        
        print(f"Application AI en lot : {len(fichiers_source)} fichiers")
        
        # Créer la structure de sortie
        dossier_sortie, mapping_fichiers = creer_structure_sortie(
            fichiers_source, 
            "transformations_ai_batch"
        )
        if not dossier_sortie:
            return False
        
        # Statistiques globales
        stats = {
            'total': len(fichiers_source),
            'reussis': 0,
            'echecs': 0,
            'transformations_totales': 0,
            'erreurs': []
        }
        
        # Traitement fichier par fichier
        for i, fichier_source in enumerate(fichiers_source, 1):
            fichier_sortie = mapping_fichiers[fichier_source]
            
            print(f"[{i}/{stats['total']}] AI : {os.path.basename(fichier_source)}")
            
            try:
                # Charger et traiter
                with open(fichier_source, 'r', encoding='utf-8') as f:
                    code_source = f.read()
                
                # Réinitialiser le moteur pour chaque fichier
                if not self.moteur.charger_code(code_source):
                    stats['echecs'] += 1
                    continue
                
                # Appliquer les instructions AI
                transformations_fichier = 0
                for instr_data in instructions_ai:
                    if self.moteur.appliquer_instruction(instr_data["instruction"]):
                        transformations_fichier += 1
                
                # Générer et sauvegarder
                code_modifie = self.moteur.generer_code_modifie()
                if code_modifie:
                    with open(fichier_sortie, 'w', encoding='utf-8') as f:
                        f.write(code_modifie)
                    
                    stats['reussis'] += 1
                    stats['transformations_totales'] += transformations_fichier
                    print(f"  ✅ {transformations_fichier} transformations appliquées")
                else:
                    stats['echecs'] += 1
                    print(f"  ❌ Échec génération code")
                
            except Exception as e:
                stats['echecs'] += 1
                stats['erreurs'].append(f"{fichier_source}: {str(e)}")
                print(f"  ❌ Erreur : {str(e)}")
        
        # Rapport final
        print("=" * 50)
        print("*** RAPPORT AI LOT ***")
        print(f"Fichiers traités : {stats['total']}")
        print(f"Succès : {stats['reussis']}")
        print(f"Échecs : {stats['echecs']}")
        print(f"Transformations totales : {stats['transformations_totales']}")
        print(f"Taux de réussite : {(stats['reussis']/stats['total']*100):.1f}%")
        
        return stats['reussis'] > 0

# 4. SÉLECTEUR JSON AI

def selectionner_json_ai():
    """Interface pour sélectionner le fichier JSON AI."""
    
    print("*** SÉLECTION JSON AI ***")
    print("=" * 25)
    
    # Chercher les fichiers JSON dans le répertoire actuel
    fichiers_json = []
    try:
        for fichier in os.listdir('.'):
            if fichier.endswith('.json') and ('transform' in fichier.lower() or 'ai' in fichier.lower()):
                fichiers_json.append(fichier)
    except:
        pass
    
    if fichiers_json:
        print("Fichiers JSON AI détectés :")
        for i, fichier in enumerate(fichiers_json, 1):
            try:
                taille = format_taille(os.path.getsize(fichier))
                print(f"  {i}. {fichier} ({taille})")
            except:
                print(f"  {i}. {fichier}")
        
        print(f"  {len(fichiers_json) + 1}. Autre fichier...")
        
        try:
            choix = input(f"\nChoisir JSON AI (1-{len(fichiers_json) + 1}) : ").strip()
            choix_num = int(choix)
            
            if 1 <= choix_num <= len(fichiers_json):
                return fichiers_json[choix_num - 1]
            elif choix_num == len(fichiers_json) + 1:
                # Sélection manuelle
                return input("Chemin du fichier JSON AI : ").strip()
        except (ValueError, KeyboardInterrupt):
            pass
    
    # Sélection manuelle par défaut
    return input("Chemin du fichier JSON AI : ").strip()

# 5. INTÉGRATION DANS LA DÉMONSTRATION

def demo_avec_json_ai():
    """Démonstration avec consommation de JSON AI."""
    
    print("*** DÉMONSTRATION AVEC JSON AI ***")
    print("=" * 40)
    
    # Étape 1 : Sélection des fichiers source
    print("ÉTAPE 1 : Sélection des fichiers à transformer")
    fichiers_cibles = launch_file_selector_with_fallback()
    
    if not fichiers_cibles:
        print("X Aucun fichier sélectionné")
        return
    
    # Étape 2 : Sélection du JSON AI
    print("\nÉTAPE 2 : Sélection du fichier JSON AI")
    chemin_json = selectionner_json_ai()
    
    if not chemin_json or not os.path.exists(chemin_json):
        print("X Fichier JSON AI non trouvé")
        return
    
    # Étape 3 : Aperçu de la configuration
    print(f"\n*** CONFIGURATION FINALE ***")
    print(f"• Fichiers source : {len(fichiers_cibles)}")
    print(f"• JSON AI : {os.path.basename(chemin_json)}")
    
    for i, fichier in enumerate(fichiers_cibles[:3], 1):
        print(f"  {i}. {os.path.basename(fichier)}")
    if len(fichiers_cibles) > 3:
        print(f"  ... et {len(fichiers_cibles) - 3} autres")
    
    # Confirmation
    confirmer = input(f"\nConfirmer le traitement AI ? (o/N) : ").strip().lower()
    if confirmer not in ['o', 'oui', 'y', 'yes']:
        print("X Traitement annulé")
        return
    
    # Étape 4 : Exécution
    print("\n*** EXÉCUTION TRANSFORMATION AI ***")
    orchestrateur_ai = OrchestrateurAI(mode_colab=True)
    
    success = orchestrateur_ai.appliquer_json_ai(fichiers_cibles, chemin_json)
    
    if success:
        print("*** TRAITEMENT AI RÉUSSI ! ***")
        gerer_sortie_environnement(None, "ai")
    else:
        print("X Le traitement AI a échoué")
    
    input("\nAppuyez sur Entrée pour continuer...")

# 6. EXEMPLE DE JSON AI POUR TESTS

EXEMPLE_JSON_AI = {
    "version": "1.0", 
    "timestamp": "2024-01-15T10:30:00Z",
    "source_analysis": {
        "files_analyzed": ["exemple.py"],
        "total_functions": 3,
        "total_classes": 0,
        "complexity_score": 4.2
    },
    "transformations": [
        {
            "id": "logging_import",
            "type": "global_import", 
            "description": "Ajouter import logging",
            "priority": 1,
            "instruction": {
                "type": "ajout",
                "contexte": "global",
                "position": "debut", 
                "remplacement": "# Transformé par AI\\nimport logging\\nlogging.basicConfig(level=logging.INFO)"
            }
        },
        {
            "id": "print_to_logging",
            "type": "function_modification",
            "description": "Remplacer print par logging.info",
            "priority": 2,
            "instruction": {
                "type": "substitution",
                "contexte": "global",
                "cible": "print",
                "remplacement": "logging.info"
            }
        }
    ],
    "validation_rules": [
        {"rule": "syntax_check", "enabled": True},
        {"rule": "import_check", "enabled": True}
    ]
}

def creer_exemple_json_ai():
    """Crée un fichier JSON AI d'exemple pour les tests."""
    nom_fichier = "exemple_transformations_ai.json"
    
    with open(nom_fichier, 'w', encoding='utf-8') as f:
        json.dump(EXEMPLE_JSON_AI, f, indent=2, ensure_ascii=False)
    
    print(f"+ Exemple JSON AI créé : {nom_fichier}")
    return nom_fichier
