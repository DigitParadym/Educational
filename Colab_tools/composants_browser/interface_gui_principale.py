#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface GUI Principale - Version Neuve Fonctionnelle
Connexion directe au TransformationLoader - Garantie de fonctionnement
"""

import sys
import os
from pathlib import Path
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Ajouter le repertoire parent au path
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

class InterfaceAST:
    """Interface graphique pour les transformations AST."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interface AST - Transformations Modulaires")
        self.root.geometry("800x600")
        
        self.fichiers_selectionnes = []
        self.transformations_disponibles = []
        self.loader = None
        
        self.creer_interface()
        self.init_transformation_loader()
    
    def creer_interface(self):
        """Cree l'interface utilisateur."""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Titre
        tk.Label(main_frame, text="Interface AST - Transformations Modulaires", 
                font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Section fichiers
        files_frame = tk.LabelFrame(main_frame, text="Fichiers", font=('Arial', 12, 'bold'))
        files_frame.pack(fill='x', pady=(0, 10))
        
        buttons_frame = tk.Frame(files_frame)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(buttons_frame, text="Selectionner Fichiers",
                 command=self.select_files).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="Selectionner Dossier",
                 command=self.select_folder).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="Effacer",
                 command=self.clear_selection).pack(side='left', padx=(0, 10))
        tk.Button(buttons_frame, text="JSON", command=self.load_json).pack(side='left')
        
        self.files_listbox = tk.Listbox(files_frame, height=4)
        self.files_listbox.pack(fill='x', padx=10, pady=(0, 10))
        
        # Section transformations
        transform_frame = tk.LabelFrame(main_frame, text="Transformations", font=('Arial', 12, 'bold'))
        transform_frame.pack(fill='x', pady=(0, 10))
        
        self.transformation_var = tk.StringVar()
        self.transformation_combo = ttk.Combobox(transform_frame, textvariable=self.transformation_var, state="readonly")
        self.transformation_combo.pack(fill='x', padx=10, pady=10)
        
        # Bouton d'application
        tk.Button(main_frame, text="Appliquer la Transformation",
                 command=self.apply_transformation,
                 font=('Arial', 12, 'bold'), bg='#27ae60', fg='white').pack(pady=10)
        
        # Console
        console_frame = tk.LabelFrame(main_frame, text="Console", font=('Arial', 12, 'bold'))
        console_frame.pack(fill='both', expand=True)
        
        self.console_text = tk.Text(console_frame, font=('Courier', 9))
        scrollbar = tk.Scrollbar(console_frame, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=scrollbar.set)
        
        self.console_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
        
        self.log_message("=== Interface AST demarree ===")
    
    def init_transformation_loader(self):
        """Initialise le TransformationLoader directement."""
        try:
            from core.transformation_loader import TransformationLoader
            
            self.loader = TransformationLoader()
            self.log_message("+ TransformationLoader cree")
            
            # Recuperer les transformations
            plugin_names = self.loader.list_transformations()
            self.log_message(f"+ {len(plugin_names)} plugins detectes")
            
            # Construire la liste pour l'interface
            self.transformations_disponibles = []
            for plugin_name in plugin_names:
                transformer = self.loader.get_transformation(plugin_name)
                if transformer:
                    metadata = transformer.get_metadata()
                    self.transformations_disponibles.append({
                        'name': plugin_name,
                        'display_name': metadata.get('name', plugin_name),
                        'description': metadata.get('description', 'Transformation'),
                        'version': metadata.get('version', '1.0')
                    })
                    self.log_message(f"  - {metadata.get('name', plugin_name)} v{metadata.get('version', '1.0')}")
            
            self.log_message(f"+ {len(self.transformations_disponibles)} transformations disponibles")
            
            # Mettre a jour la liste
            self.update_transformations_list()
            
        except Exception as e:
            self.log_message(f"X Erreur TransformationLoader: {e}")
            import traceback
            self.log_message(f"X Details: {traceback.format_exc()}")
            self.transformations_disponibles = []
    
    def update_transformations_list(self):
        """Met a jour la liste des transformations."""
        try:
            values = []
            if self.transformations_disponibles:
                for t in self.transformations_disponibles:
                    display_text = f"{t['display_name']} - {t['description']}"
                    values.append(display_text)
                
                self.log_message(f"+ Liste mise a jour: {len(values)} transformations")
            else:
                values = ["Aucune transformation disponible"]
                self.log_message("! Aucune transformation disponible")
            
            self.transformation_combo['values'] = values
            if values and "Aucune" not in values[0]:
                self.transformation_combo.current(0)
                self.log_message("+ Premiere transformation selectionnee")
        
        except Exception as e:
            self.log_message(f"X Erreur mise a jour liste: {e}")
    
    def select_files(self):
        """Selectionne des fichiers."""
        fichiers = filedialog.askopenfilenames(
            title="Selectionner des fichiers Python",
            filetypes=[("Fichiers Python", "*.py"), ("Tous les fichiers", "*.*")]
        )
        
        if fichiers:
            self.fichiers_selectionnes = list(fichiers)
            self.update_files_display()
            self.log_message(f"+ {len(fichiers)} fichier(s) selectionne(s)")
    
    def select_folder(self):
        """Selectionne un dossier."""
        dossier = filedialog.askdirectory(title="Selectionner un dossier")
        
        if dossier:
            fichiers_python = []
            for root, dirs, files in os.walk(dossier):
                for file in files:
                    if file.endswith('.py'):
                        fichiers_python.append(os.path.join(root, file))
            
            if fichiers_python:
                self.fichiers_selectionnes = fichiers_python
                self.update_files_display()
                self.log_message(f"+ {len(fichiers_python)} fichier(s) Python trouve(s)")
            else:
                self.log_message("! Aucun fichier Python trouve")
    
    def clear_selection(self):
        """Efface la selection."""
        self.fichiers_selectionnes = []
        self.update_files_display()
        self.log_message("+ Selection effacee")
    
    def load_json(self):
        """Charge un fichier JSON."""
        fichier_json = filedialog.askopenfilename(
            title="Selectionner fichier JSON",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous", "*.*")]
        )
        if fichier_json:
            self.log_message(f"+ JSON charge: {os.path.basename(fichier_json)}")
    
    def update_files_display(self):
        """Met a jour l'affichage des fichiers."""
        self.files_listbox.delete(0, tk.END)
        for fichier in self.fichiers_selectionnes:
            self.files_listbox.insert(tk.END, os.path.basename(fichier))
    
    def apply_transformation(self):
        """Applique la transformation selectionnee."""
        if not self.fichiers_selectionnes:
            self.log_message("X Aucun fichier selectionne")
            return
        
        if not self.loader or not self.transformations_disponibles:
            self.log_message("X Aucune transformation disponible")
            return
        
        selection = self.transformation_combo.current()
        if selection == -1:
            self.log_message("X Aucune transformation selectionnee")
            return
        
        transformation = self.transformations_disponibles[selection]
        transformation_name = transformation['name']
        
        self.log_message("=== DEBUT TRANSFORMATION ===")
        self.log_message(f"Transformation: {transformation['display_name']}")
        
        # Creer dossier de sortie
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dossier_sortie = f"transformations_gui_{timestamp}"
        os.makedirs(dossier_sortie, exist_ok=True)
        
        succes = 0
        echecs = 0
        
        for i, fichier_source in enumerate(self.fichiers_selectionnes, 1):
            self.log_message(f"[{i}/{len(self.fichiers_selectionnes)}] {os.path.basename(fichier_source)}")
            
            try:
                # Lire le fichier source
                with open(fichier_source, 'r', encoding='utf-8') as f:
                    code_source = f.read()
                
                # Appliquer la transformation
                transformer = self.loader.get_transformation(transformation_name)
                if transformer and transformer.can_transform(code_source):
                    code_transforme = transformer.transform(code_source)
                    
                    # Sauvegarder
                    nom_base = os.path.splitext(os.path.basename(fichier_source))[0]
                    fichier_sortie = os.path.join(dossier_sortie, f"{nom_base}_{transformation_name}.py")
                    
                    with open(fichier_sortie, 'w', encoding='utf-8') as f:
                        f.write(code_transforme)
                    
                    succes += 1
                    self.log_message("  + Reussi")
                else:
                    echecs += 1
                    self.log_message("  - Non applicable")
                    
            except Exception as e:
                echecs += 1
                self.log_message(f"  X Erreur: {e}")
        
        self.log_message("=== RESUME ===")
        self.log_message(f"Succes: {succes}, Echecs: {echecs}")
        self.log_message(f"Dossier: {dossier_sortie}")
    
    def log_message(self, message):
        """Ajoute un message a la console."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.console_text.insert(tk.END, full_message)
        self.console_text.see(tk.END)
        self.root.update_idletasks()
        print(message)
    
    def run(self):
        """Lance l'interface."""
        try:
            self.log_message("Interface graphique demarree")
            self.root.mainloop()
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False

def main():
    """Point d'entree principal."""
    try:
        app = InterfaceAST()
        app.run()
    except Exception as e:
        print(f'Erreur: {e}')
        input('Appuyez sur Entree pour fermer...')

if __name__ == '__main__':
    main()
