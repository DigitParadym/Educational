"""Utilitaires pour les tests."""

def calculer(operation, *args):
    if operation == "somme":
        return sum(args)
    elif operation == "produit":
        result = 1
        for arg in args:
            result *= arg
        return result
    else:
        raise ValueError("Operation non supportee")

def formatter_texte(texte, majuscule=False):
    if majuscule:
        return texte.upper()
    return texte.lower()
