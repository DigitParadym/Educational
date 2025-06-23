# ===============================================
# MODIFICATIONS NÉCESSAIRES POUR modificateur_interactif.py
# ===============================================

"""
Instructions pour modifier votre fichier modificateur_interactif.py :

1. AJOUTER la fonction wrapper après la ligne ~420 (après browser_fichier_interactif)
2. REMPLACER la fonction demo_simple() par demo() (ligne ~1050)
3. MODIFIER le menu principal (ligne ~1170)
4. MODIFIER la fonction main() (ligne ~1200)

Voici les modifications exactes :
"""

# ===============================================
# MODIFICATION 1 : AJOUTER APRÈS LA LIGNE ~420
# Ajoutez cette fonction après browser_fichier_interactif()
# ===============================================

def launch_file_selector_with_fallback():
    """Lance le sélecteur GUI avec fallback vers le browser existant."""
    try:
        from composants_browser.file_selector_ui import launch_file_selector_integrated
        
        fichiers_python = launch_file_selector_integrated()
        
        if fichiers_python:
            print(f"+ Interface GUI : {len(fichiers_python)} fichier(s) sélectionné(s)")
            return fichiers_python
        else:
            print("! Aucune sélection GUI, retour au browser texte...")
            fichier_unique = browser_fichier_interactif()
            return [fichier_unique] if fichier_unique else []
        
    except Exception as e:
        print(f"! Interface GUI non disponible ({e}), utilisation du browser texte...")
        fichier_unique = browser_fichier_interactif()
        return [fichier_unique] if fichier_unique else []

# ===============================================
# MODIFICATION 2 : REMPLACER demo_simple() PAR demo()
# Trouvez la fonction demo_simple() (ligne ~1050) et remplacez-la ENTIÈREMENT par :
# ===============================================

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

# ===============================================
# MODIFICATION 3 : AJOUTER cette fonction après demo()
# ===============================================

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

# ===============================================
# MODIFICATION 4 : MODIFIER LE MENU PRINCIPAL
# Trouvez la fonction menu_principal() (ligne ~1170) et remplacez-la par :
# ===============================================

def menu_principal():
    """Affiche le menu principal avec les options de démonstration."""
    print("*** OUTIL DE REFONTE AST - VERSION 2.4 ***")
    print("=" * 50)
    print("Bienvenue dans l'outil de transformation de code Python par AST !")
    print("")
    print("*** MODES DISPONIBLES :")
    print("=" * 25)
    print("1. Démonstration")  # ← Renommé depuis "Démonstration Simple"
    print("   → Interface GUI + traitement fichier unique ou lot")
    print("   → Browser interactif avec fallback automatique")
    print("")
    print("2. Démonstration AI")  # ← NOUVEAU
    print("   → Transformations pilotées par fichier JSON AI")
    print("   → Support des instructions AI complexes")
    print("")
    print("3. Mode Session Interactive")
    print("   → Création de recettes personnalisées")
    print("   → Contrôle total des transformations")
    print("")
    print("4. Quitter")
    print("=" * 50)
    
    try:
        choix = input("Votre choix (1-4): ").strip()
        return choix
    except KeyboardInterrupt:
        print("\nAu revoir !")
        return "4"

# ===============================================
# MODIFICATION 5 : MODIFIER LA FONCTION main()
# Trouvez la fonction main() (ligne ~1200) et modifiez la section des choix :
# ===============================================

# Dans la fonction main(), remplacez la boucle while True par :

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
    
    # Mode interactif avec menu
    while True:
        choix = menu_principal()
        
        if choix == "1":
            print("*** LANCEMENT : DÉMONSTRATION ***")  # ← Modifié
            print("=" * 40)
            demo()  # ← Renommé depuis demo_simple()
            
        elif choix == "2":  # ← NOUVEAU
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
            
        elif choix == "3":  # ← Numérotation modifiée
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
                
        elif choix == "4":  # ← Numérotation modifiée
            print("Merci d'avoir utilisé l'Outil de Refonte AST !")
            print("Au revoir ! 👋")
            break
            
        else:
            print("X Choix invalide. Veuillez choisir entre 1 et 4.")
            input("Appuyez sur Entrée pour continuer...")

# ===============================================
# RÉSUMÉ DES MODIFICATIONS
# ===============================================

"""
RÉSUMÉ DES CHANGEMENTS À APPORTER :

1. AJOUTER launch_file_selector_with_fallback() après ligne ~420
2. REMPLACER demo_simple() par demo() (ligne ~1050)  
3. AJOUTER gerer_sortie_environnement() après demo()
4. REMPLACER menu_principal() (ligne ~1170)
5. MODIFIER main() pour supporter l'option 2 (ligne ~1200)

Total : ~150 lignes ajoutées/modifiées sur 1200+ lignes

AVANTAGES :
✅ Interface GUI moderne avec sélection multiple
✅ Support JSON AI pour transformations pilotées par IA
✅ Traitement en lot automatique
✅ Fallback intelligent vers l'interface texte
✅ Gestion optimisée selon l'environnement (Colab/VSCode/Terminal)
✅ Architecture modulaire et extensible
"""