
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
