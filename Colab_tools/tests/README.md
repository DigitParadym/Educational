# Tests AST Modulaire

## Structure

```
tests/
├── scripts/          # Scripts de test
│   ├── unittests/   # Tests unitaires
│   ├── integration/ # Tests d'integration
│   └── performance/ # Tests de performance
├── data/            # Donnees de test
│   ├── input/       # Fichiers Python d'entree
│   ├── expected/    # Resultats attendus
│   ├── json_configs/# Configurations JSON
│   └── invalid/     # Fichiers invalides
├── output/          # Resultats des tests
│   ├── transformations/ # Fichiers transformes
│   ├── reports/     # Rapports
│   └── logs/        # Logs
└── config/          # Configuration

## Utilisation

### Tests automatiques
```bash
python tests/run_tests.py --auto
```

### Menu interactif
```bash
python tests/run_tests.py
```

### Tests unitaires uniquement
```bash
python -m unittest discover tests/scripts/unittests/
```

## Fichiers de test inclus

- simple_example.py : Code avec print() pour transformation
- no_docstrings.py : Code sans documentation
- simple_transform.json : Configuration de transformation
- syntax_error.py : Fichier avec erreur pour tests

## Tests disponibles

1. Test Imports : Verifie les imports essentiels
2. Test Systeme Core : Teste le chargeur de plugins
3. Test Interface GUI : Teste l'interface graphique
4. Tests Unitaires : Suite complete de tests
5. Lancement Interface : Lance l'interface complete

## Resultats

Les resultats sont sauvegardes dans output/ :
- Transformations dans transformations/
- Rapports dans reports/
- Logs dans logs/

## Commandes utiles

### Lancer tous les tests
```bash
python tests/run_tests.py --auto
```

### Generer un rapport
```bash
python tests/scripts/generate_report.py
```

## Configuration

Editer config/test_settings.json pour personnaliser

## Troubleshooting

### Erreur d'import
- Verifier que le chemin racine est correct
- S'assurer que __init__.py existe dans les dossiers

### Tests qui echouent
- Verifier les dependances
- Lancer en mode debug : python tests/run_tests.py --debug
