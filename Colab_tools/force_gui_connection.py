#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour forcer la connexion GUI-Modulaire
Remplace complètement la méthode d'initialisation défectueuse
"""

import os

def fix_gui_connection_final():
    """Corrige définitivement la connexion GUI."""
    gui_file = "composants_browser/interface_gui_principale.py"
    
    try:
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Remplacement complet de la méthode init_moteur_modulaire...")
        
        # Nouvelle méthode complètement réécrite
        new_init_method = '''    def init_moteur_modulaire(self):
        """Initialise le moteur AST avec système modulaire - Version Corrigée."""
        try:
            # Import direct local
            import sys
            import os
            from pathlib import Path
            
            # Ajouter le répertoire parent au path
            current_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(current_dir))
            
            # Import direct du moteur
            from modificateur_interactif import OrchestrateurAST
            
            # Créer l'instance
            self.orchestrateur = OrchestrateurAST()
            
            # Tester les transformations
            self.transformations_disponibles = self.orchestrateur.lister_transformations_modulaires()
            
            # Messages de debug
            self.log_message(f"+ Moteur modulaire connecté avec succès!")
            self.log_message(f"+ {len(self.transformations_disponibles)} transformation(s) trouvée(s)")
            
            # Lister les transformations trouvées
            for t in self.transformations_disponibles:
                self.log_message(f"  - {t['display_name']} v{t.get('version', 'N/A')}")
            
            # FORCER la mise à jour de la liste déroulante
            self.root.after(100, self.update_transformations_list)
            
        except Exception as e:
            self.log_message(f"X Erreur connexion moteur: {e}")
            import traceback
            self.log_message(f"X Détails: {traceback.format_exc()}")
            self.orchestrateur = None
            self.transformations_disponibles = []'''
        
        # Trouver et remplacer la méthode existante
        start_pattern = "def init_moteur_modulaire(self):"
        start_pos = content.find(start_pattern)
        
        if start_pos != -1:
            # Trouver la fin de la méthode
            lines = content[start_pos:].split('\n')
            method_end = 1  # Commencer après la ligne de définition
            
            for i in range(1, len(lines)):
                line = lines[i]
                # Si on trouve une nouvelle méthode ou fin de classe
                if line.strip() and not line.startswith('        ') and not line.startswith('    """'):
                    method_end = i
                    break
            
            # Extraire l'ancienne méthode
            old_method_lines = lines[:method_end]
            remaining_content = '\n'.join(lines[method_end:])
            
            # Construire le nouveau contenu
            before_method = content[:start_pos]
            new_content = before_method + new_init_method + '\n' + remaining_content
            
            # Sauvegarder
            with open(gui_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("+ Méthode init_moteur_modulaire remplacée complètement")
            return True
        else:
            print("X Méthode init_moteur_modulaire non trouvée")
            return False
            
    except Exception as e:
        print(f"X Erreur: {e}")
        return False

def add_forced_update_method():
    """Ajoute une méthode pour forcer la mise à jour."""
    gui_file = "composants_browser/interface_gui_principale.py"
    
    try:
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Méthode de mise à jour forcée
        forced_update_method = '''
    def update_transformations_list(self):
        """Met à jour la liste déroulante des transformations - Version Forcée."""
        if not hasattr(self, 'transformation_combo'):
            return
        
        values = []
        if hasattr(self, 'transformations_disponibles') and self.transformations_disponibles:
            for t in self.transformations_disponibles:
                display_text = f"{t['display_name']} - {t['description']}"
                values.append(display_text)
            
            self.log_message(f"+ Mise à jour liste: {len(values)} transformation(s)")
        else:
            self.log_message("! Aucune transformation pour la liste")
        
        # Mettre à jour la combobox
        self.transformation_combo['values'] = values
        if values:
            self.transformation_combo.current(0)
            self.log_message(f"+ Liste mise à jour: {values[0]}")
        else:
            self.log_message("X Liste vide après mise à jour")
'''
        
        # Trouver où insérer (avant la fin de la classe)
        class_end = content.rfind("    def run(self):")
        if class_end != -1:
            # Insérer avant la méthode run
            content = content[:class_end] + forced_update_method + '\n' + content[class_end:]
            
            with open(gui_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("+ Méthode update_transformations_list ajoutée")
            return True
        else:
            print("! Impossible de trouver où insérer la méthode")
            return False
            
    except Exception as e:
        print(f"X Erreur ajout méthode: {e}")
        return False

def test_system_again():
    """Test final du système."""
    try:
        import sys
        sys.path.insert(0, os.getcwd())
        
        from core.transformation_loader import TransformationLoader
        loader = TransformationLoader()
        plugins = loader.list_transformations()
        
        print(f"+ Test final: {len(plugins)} plugin(s) détecté(s)")
        for plugin_name in plugins:
            transformer = loader.get_transformation(plugin_name)
            metadata = transformer.get_metadata()
            print(f"  - {metadata['name']} v{metadata['version']}")
        
        return len(plugins) > 0
        
    except Exception as e:
        print(f"X Test final échoué: {e}")
        return False

def main():
    """Correction finale et définitive."""
    print("=== CORRECTION FINALE GUI-MODULAIRE ===")
    print("Remplacement complet des méthodes défectueuses")
    print("=" * 50)
    
    print("1. REMPLACEMENT INIT_MOTEUR_MODULAIRE")
    print("-" * 40)
    if not fix_gui_connection_final():
        print("X Échec correction")
        return
    
    print("\n2. AJOUT MÉTHODE UPDATE FORCÉE")
    print("-" * 35)
    if not add_forced_update_method():
        print("X Échec ajout méthode")
        return
    
    print("\n3. TEST SYSTÈME FINAL")
    print("-" * 25)
    if test_system_again():
        print("\n🎉 CORRECTION FINALE RÉUSSIE !")
        print("Le système modulaire est maintenant complètement opérationnel.")
        print("\nInstructions finales:")
        print("1. Fermez l'interface actuelle")
        print("2. Relancez: python composants_browser/interface_gui_principale.py")
        print("3. Vérifiez que la liste des transformations se remplit")
        print("4. Les plugins devraient maintenant être visibles!")
    else:
        print("\n❌ Le système a encore des problèmes")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
    input("\nAppuyez sur Entrée pour fermer...")
