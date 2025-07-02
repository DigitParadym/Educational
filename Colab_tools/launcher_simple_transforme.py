import logging

"""
Lanceur simple pour l'outil AST - Compatible Windows
Version complete avec detection d'environnement
"""
import sys
import os
COLAB_ENV = False
VSCODE_ENV = False
try:
    import google.colab
    from google.colab import files
    COLAB_ENV = True
    logging.info('*** Environnement Google Colab detecte ***')
except ImportError:
    pass
try:
    if 'VSCODE_PID' in os.environ or 'JUPYTER_SERVER_ROOT' in os.environ:
        VSCODE_ENV = True
        logging.info('*** Environnement VSCode/Jupyter detecte ***')
except:
    pass
if not COLAB_ENV and (not VSCODE_ENV):
    logging.info('*** Environnement Terminal detecte ***')

def main():
    """Point d'entree principal."""
    logging.info(">> Lancement de l'interface graphique AST...")
    try:
        from composants_browser.interface_gui_principale import InterfaceAST
        logging.info('+ Interface GUI trouvee')
        app = InterfaceAST()
        logging.info('+ Interface creee, lancement...')
        success = app.run()
        if success:
            logging.info('+ Interface fermee normalement')
        else:
            logging.info('! Interface fermee avec avertissements')
    except ImportError as e:
        logging.info(f'X Erreur import GUI: {e}')
        logging.info('>> Fallback vers modificateur_interactif.py...')
        try:
            import modificateur_interactif
            modificateur_interactif.main()
        except Exception as e2:
            logging.info(f'X Erreur fallback: {e2}')
            logging.info('>> Utilisation du fallback simple...')
            fallback_simple()
    except Exception as e:
        logging.info(f'X Erreur generale: {e}')
        logging.info(">> Diagnostic de l'environnement...")
        diagnostic_environnement()

def fallback_simple():
    """Fallback simple en cas d'echec total."""
    logging.info('=' * 50)
    logging.info('MODE FALLBACK SIMPLE')
    logging.info('=' * 50)
    logging.info('Aucune interface disponible')
    logging.info('')
    logging.info('Solutions possibles:')
    logging.info('1. Verifiez que tkinter est installe')
    logging.info('2. Testez: python -m tkinter')
    logging.info('3. Reinstallez Python avec tkinter')
    logging.info("4. Utilisez l'interface en ligne de commande")
    logging.info('=' * 50)
    reponse = input('Voulez-vous tenter un diagnostic? (o/N): ').strip().lower()
    if reponse in ['o', 'oui', 'y', 'yes']:
        diagnostic_environnement()

def diagnostic_environnement():
    """Diagnostic de l'environnement."""
    logging.info('\n' + '=' * 40)
    logging.info("DIAGNOSTIC DE L'ENVIRONNEMENT")
    logging.info('=' * 40)
    logging.info(f'Python version: {sys.version}')
    logging.info(f'Python executable: {sys.executable}')
    logging.info(f'Repertoire actuel: {os.getcwd()}')
    logging.info(f'COLAB detecte: {('Oui' if COLAB_ENV else 'Non')}')
    logging.info(f'VSCODE detecte: {('Oui' if VSCODE_ENV else 'Non')}')
    try:
        import tkinter
        logging.info(f'Tkinter: OK (version {tkinter.TkVersion})')
        try:
            root = tkinter.Tk()
            root.withdraw()
            root.destroy()
            logging.info('Test fenetre tkinter: OK')
        except Exception as e:
            logging.info(f'Test fenetre tkinter: ECHEC ({e})')
    except ImportError as e:
        logging.info(f'Tkinter: ERREUR - {e}')
        logging.info('Solution: Reinstallez Python avec tkinter')
    modules_requis = ['os', 'sys', 'datetime', 'pathlib', 'traceback']
    logging.info('\nModules requis:')
    for module in modules_requis:
        try:
            __import__(module)
            logging.info(f'  {module}: OK')
        except ImportError:
            logging.info(f'  {module}: MANQUANT')
    logging.info('\nFichiers du projet:')
    fichiers_attendus = ['launcher_simple.py', 'modificateur_interactif.py', 'composants_browser/interface_gui_principale.py', 'composants_browser/__init__.py']
    for fichier in fichiers_attendus:
        if os.path.exists(fichier):
            taille = os.path.getsize(fichier)
            logging.info(f'  {fichier}: OK ({taille} bytes)')
        else:
            logging.info(f'  {fichier}: MANQUANT')
    logging.info('=' * 40)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nArret par l'utilisateur")
    except Exception as e:
        logging.info(f'\nErreur critique: {e}')
        diagnostic_environnement()
        input('\nAppuyez sur Entree pour fermer...')