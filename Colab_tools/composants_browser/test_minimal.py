#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test minimal pour vérifier l'affichage des fenêtres Tkinter
Compatible Windows/MINGW64
"""

import tkinter as tk
import sys
import os

def test_affichage_gui():
    """Test d'affichage d'une fenêtre GUI simple."""
    
    print("=" * 50)
    print("TEST MINIMAL D'AFFICHAGE GUI")
    print("=" * 50)
    
    try:
        print("[1/5] Creation de la fenetre...")
        root = tk.Tk()
        
        print("[2/5] Configuration de la fenetre...")
        root.title("Test Fenetre - AST Tool")
        root.geometry("500x400")
        
        # FORCER L'AFFICHAGE - IMPORTANT POUR WINDOWS
        print("[3/5] Forcage de l'affichage...")
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()
        
        # Centrer la fenêtre
        root.update_idletasks()
        width = 500
        height = 400
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        print("[4/5] Ajout du contenu...")
        
        # Titre principal
        titre = tk.Label(root, 
                        text="TEST D'AFFICHAGE REUSSI !", 
                        font=("Arial", 18, "bold"),
                        fg="green",
                        pady=20)
        titre.pack()
        
        # Message d'information
        info = tk.Label(root, 
                       text="Si vous voyez cette fenetre,\nvotre environnement GUI fonctionne !",
                       font=("Arial", 12),
                       pady=10)
        info.pack()
        
        # Informations système
        sys_info = tk.Label(root,
                           text=f"Python : {sys.version[:6]}\n"
                                f"Systeme : {os.name}\n"
                                f"Repertoire : {os.getcwd()}",
                           font=("Courier", 9),
                           fg="blue",
                           pady=10)
        sys_info.pack()
        
        # Instructions
        instructions = tk.Label(root,
                               text="INSTRUCTIONS :\n"
                                    "• Si cette fenetre apparait = GUI OK !\n"
                                    "• Sinon, verifiez Alt+Tab\n"
                                    "• Regardez la barre des taches\n"
                                    "• Cliquez 'Fermer' pour continuer",
                               font=("Arial", 10),
                               fg="navy",
                               pady=15,
                               justify=tk.LEFT)
        instructions.pack()
        
        # Bouton de fermeture
        bouton_fermer = tk.Button(root, 
                                 text="FERMER ET CONTINUER",
                                 command=root.destroy,
                                 font=("Arial", 14, "bold"),
                                 bg="lightblue",
                                 pady=10,
                                 width=20)
        bouton_fermer.pack(pady=20)
        
        # Retirer topmost après 2 secondes
        root.after(2000, lambda: root.attributes('-topmost', False))
        
        print("[5/5] Lancement de l'interface...")
        print("\n" + "=" * 50)
        print("CHERCHEZ LA FENETRE :")
        print("• Verifiez votre barre des taches")
        print("• Appuyez Alt+Tab pour voir toutes les fenetres")
        print("• La fenetre peut etre derriere d'autres fenetres")
        print("• Icone Python peut clignoter dans la barre des taches")
        print("=" * 50)
        
        # Démarrer la boucle principale
        root.mainloop()
        
        print("\n[OK] Fenetre fermee - Test termine avec succes !")
        return True
        
    except Exception as e:
        print(f"\n[ERREUR] Probleme GUI : {e}")
        print("Votre environnement ne supporte pas l'interface graphique")
        return False

def diagnostiquer_environnement():
    """Diagnostic de l'environnement avant le test."""
    
    print("DIAGNOSTIC DE L'ENVIRONNEMENT :")
    print("-" * 30)
    
    # Python
    print(f"Python : {sys.version}")
    print(f"Executable : {sys.executable}")
    
    # Système
    print(f"OS : {os.name}")
    print(f"Repertoire : {os.getcwd()}")
    
    # Variables d'environnement importantes
    display = os.environ.get('DISPLAY', 'Non definie')
    print(f"DISPLAY : {display}")
    
    # Test Tkinter
    try:
        import tkinter
        print(f"Tkinter : OK (version {tkinter.TkVersion})")
    except ImportError as e:
        print(f"Tkinter : ERREUR - {e}")
        return False
    
    print("-" * 30)
    return True

if __name__ == "__main__":
    print("DEMARRAGE DU TEST MINIMAL GUI")
    print("=" * 50)
    
    # Diagnostic préliminaire
    if not diagnostiquer_environnement():
        print("\n[ECHEC] Environnement non compatible")
        input("Appuyez sur Entree pour fermer...")
        sys.exit(1)
    
    # Test d'affichage
    print("\nLancement du test d'affichage...")
    
    try:
        succes = test_affichage_gui()
        
        if succes:
            print("\n" + "=" * 50)
            print("RESULTAT : TEST REUSSI !")
            print("Votre environnement supporte l'interface graphique.")
            print("Vous pouvez maintenant utiliser l'interface AST complete.")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("RESULTAT : TEST ECHOUE")
            print("Probleme avec l'affichage GUI")
            print("=" * 50)
            
    except KeyboardInterrupt:
        print("\n[STOP] Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n[ERREUR] Erreur inattendue : {e}")
    
    input("\nAppuyez sur Entree pour fermer...")
