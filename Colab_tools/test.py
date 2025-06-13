# ===== Fichier de test pour l'outil de refonte AST =====

# --- Variables Globales ---
APP_NAME = "Mon Application"
VERSION = 1
DEBUG_MODE = False

# --- Fonctions ---

def demarrer_app():
    """
    Affiche un message de démarrage avec le nom de l'application.
    """
    print("-------------------------")
    print(f"Lancement de {APP_NAME}...")
    
    if DEBUG_MODE:
        print("!! ATTENTION: Mode debug activé !!")

def calculer(a, b):
    """
    Une fonction de calcul simple.
    """
    resultat = a + b
    print(f"Le résultat du calcul est : {resultat}")
    return resultat

# --- Bloc Principal ---

if __name__ == "__main__":
    demarrer_app()
    
    valeur1 = 10
    valeur2 = 25
    
    calculer(valeur1, valeur2)
    
    print("\nScript terminé.")
    print(f"Version: {VERSION}")

