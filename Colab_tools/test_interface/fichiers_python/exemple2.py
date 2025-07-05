"""Second fichier exemple pour les tests."""

import sys
import os

def traiter_donnees(donnees):
    resultat = []
    for item in donnees:
        if item > 0:
            resultat.append(item * 2)
    return resultat

def fonction_complexe(a, b, c=None):
    if c is None:
        c = []
    
    temp = a + b
    if temp > 10:
        c.append(temp)
    
    return c

# Variables globales
CONSTANTE = 42
config = {"debug": True, "version": "1.0"}
