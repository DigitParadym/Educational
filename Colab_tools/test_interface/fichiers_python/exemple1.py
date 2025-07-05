#!/usr/bin/env python3
"""Module exemple 1 pour tester les transformations."""

def fonction_simple(x, y):
    result = x + y
    return result

def autre_fonction():
    print("Hello world")
    data = [1, 2, 3, 4, 5]
    for item in data:
        print(item)

class ExempleClasse:
    def __init__(self, nom):
        self.nom = nom
    
    def afficher(self):
        print(f"Nom: {self.nom}")

if __name__ == "__main__":
    obj = ExempleClasse("Test")
    obj.afficher()
