#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Correctif cible pour la ligne 1428 qui contient l'emoji problematique
"""

def fix_line_1428_specifically():
    """Corrige specifiquement la ligne 1428 qui pose probleme."""
    
    file_path = "modificateur_interactif.py"
    
    try:
        # Lire toutes les lignes
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Fichier lu: {len(lines)} lignes")
        
        # Backup avant modification
        with open(file_path + ".fix_backup", 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Backup cree: modificateur_interactif.py.fix_backup")
        
        # Chercher et corriger la ligne 1428 (index 1427)
        line_1428_index = 1427  # Les listes commencent a 0
        
        if line_1428_index < len(lines):
            original_line = lines[line_1428_index]
            print(f"Ligne 1428 originale trouvee")
            
            # Verifier que c'est bien la ligne problematique
            if "Lancement" in original_line and "interface" in original_line:
                # Remplacer par la version ASCII
                lines[line_1428_index] = '    print(">> Lancement de l\'interface graphique...")\n'
                print("Ligne 1428 corrigee avec succes")
                
                # Sauvegarder le fichier corrige
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print("Fichier sauvegarde avec la correction")
                return True
            else:
                print("La ligne 1428 ne correspond pas au pattern attendu")
                print(f"Contenu: {original_line.strip()}")
                return False
        else:
            print(f"Le fichier n'a que {len(lines)} lignes, impossible d'acceder a la ligne 1428")
            return False
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def apply_all_unicode_fixes():
    """Applique tous les correctifs Unicode necessaires."""
    
    file_path = "modificateur_interactif.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("Application de tous les correctifs Unicode...")
        
        # Correctifs cibles
        fixes = [
            # Emojis dans le code
            ('>>', '>>'),  # Fusee
            ('>>', '>>'),   # Fusee (version directe)
            ('>>', '>>'),           # Fusee (caractere direct)
            
            ('+', '+'),   # Check vert
            ('+', '+'),
            ('+', '+'),
            
            ('X', 'X'),   # X rouge
            ('X', 'X'),
            ('X', 'X'),
            
            ('>>', '>>'),  # Clipboard
            ('>>', '>>'),
            ('>>', '>>'),
            
            ('', ''),    # Wave
            ('', ''),
            ('', ''),
        ]
        
        changes_count = 0
        for old, new in fixes:
            old_content = content
            content = content.replace(old, new)
            if content != old_content:
                changes_count += 1
                print(f"Correctif applique #{changes_count}")
        
        if changes_count > 0:
            # Backup complet
            with open(file_path + ".unicode_backup", 'w', encoding='utf-8') as f:
                with open(file_path, 'r', encoding='utf-8') as orig:
                    f.write(orig.read())
            
            # Sauvegarder les corrections
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Total: {changes_count} correctifs appliques")
            return True
        else:
            print("Aucun correctif necessaire")
            return True
            
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=== CORRECTIF CIBLE LIGNE 1428 ===")
    
    # Essayer d'abord la correction specifique
    if fix_line_1428_specifically():
        print("Correction ligne 1428 reussie!")
    else:
        print("Correction ligne 1428 echouee, tentative correctif global...")
        if apply_all_unicode_fixes():
            print("Correctifs globaux appliques!")
        else:
            print("Tous les correctifs ont echoue")
            exit(1)
    
    print("")
    print("=== TEST RAPIDE ===")
    try:
        # Test basique
        with open("modificateur_interactif.py", 'r', encoding='utf-8') as f:
            first_lines = f.readlines()[:10]
        print("Lecture du fichier corrige: OK")
        
        print("")
        print("Vous pouvez maintenant tester:")
        print("python modificateur_interactif.py")
        
    except Exception as e:
        print(f"Attention: {e}")
    
    input("\nAppuyez sur Entree pour fermer...")
