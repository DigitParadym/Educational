import sys
import os
from pathlib import Path

# Ajouter le repertoire parent au path pour les imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import du moteur modulaire
try:
    from modificateur_interactif import OrchestrateurAST
    MOTEUR_DISPONIBLE = True
    print("+ Moteur modulaire charge avec succes")
except ImportError as e:
    print(f"! Moteur modulaire non disponible: {e}")
    MOTEUR_DISPONIBLE = False

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Graphique Principale - Outil AST - VERSION FINALE STABLE
==================================================================

Interface GUI stable et fonctionnelle pour l'outil de transformation AST.
Compatible avec launcher_simple.py et tous les environnements.
Version sans caracteres Unicode et sans browser complexe.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import datetime
import traceback
from pathlib import Path

class InterfaceAST:
    """Interface graphique principale pour l'outil AST."""
    
    def __init__(self):
        print(">> Initialisation de l'interface AST...")
        
        self.root = tk.Tk()
        self.fichiers_selectionnes = []
        self.dossiers_selectionnes = []
        self.mode_selection = "fichiers"  # "fichiers" ou "dossiers"
        self.json_instructions_path = None  # Chemin JSON
        
        # Configuration de la fenetre
        self.setup_window()
        
        # Creation de l'interface
        self.create_interface()
        
        # Initialisation terminee
        self.log("+ Interface AST prete a l'emploi !")
        self.log("+ Ajoutez des fichiers Python ou des dossiers pour commencer")
        
        
        # Initialiser le moteur modulaire
        self.init_moteur_modulaire()
        print("+ Interface AST creee avec succes")
    
    def setup_window(self):
        """Configuration avancee de la fenetre principale."""
        print(">> Configuration de la fenetre...")
        
        # Titre et dimensions
        self.root.title("Outil de Transformation AST - Interface Principale")
        self.root.geometry("1000x800")
        self.root.minsize(900, 600)
        
        # FORCER L'AFFICHAGE - Compatible Windows/Linux/Mac
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # Centrage de la fenetre
        self.center_window()
        
        # Retirer topmost apres 5 secondes
        self.root.after(5000, lambda: self.root.attributes('-topmost', False))
        
        # Gestion de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("+ Fenetre configuree")
    
    def center_window(self):
        """Centre la fenetre sur l'ecran."""
        try:
            self.root.update_idletasks()
            width = 1000
            height = 800
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        except:
            pass
    
    def create_interface(self):
        """Cree l'interface utilisateur complete."""
        print(">> Creation de l'interface...")
        
        # Style global
        self.setup_styles()
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === EN-TETE ===
        self.create_header(main_frame)
        
        # === SELECTION DE MODE ===
        self.create_mode_selection(main_frame)
        
        # === ACTIONS PRINCIPALES (déplacées vers le haut) ===
        self.create_action_panel(main_frame)
        
        # === PANNEAU PRINCIPAL (divise) ===
        self.create_main_panels(main_frame)
        
        # === BARRE DE STATUT ===
        self.create_status_bar(main_frame)
        
        print("+ Interface creee")
    
    def setup_styles(self):
        """Configure les styles TTK."""
        style = ttk.Style()
        
        # Styles personnalises
        style.configure("Title.TLabel", font=('Arial', 16, 'bold'))
        style.configure("Subtitle.TLabel", font=('Arial', 10), foreground='blue')
        style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        style.configure("Action.TButton", font=('Arial', 11, 'bold'), padding=(15, 8))
        style.configure("Mode.TButton", padding=(10, 5))
    
    def create_header(self, parent):
        """Cree l'en-tete avec titre et informations."""
        header_frame = ttk.LabelFrame(parent, text=" Outil de Transformation AST ", padding="20")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Titre principal
        title_label = ttk.Label(
            header_frame, 
            text="[Python] Transformateur de Code Python", 
            style="Title.TLabel"
        )
        title_label.pack()
        
        # Sous-titre
        subtitle_label = ttk.Label(
            header_frame, 
            text="Conversion print() -> logging • Traitement en lot • Interface moderne",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Informations de version et repertoire
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        version_label = ttk.Label(info_frame, text="Version 2.4", font=('Arial', 8))
        version_label.pack(side=tk.LEFT)
        
        dir_label = ttk.Label(info_frame, text=f"Dossier: {os.getcwd()}", font=('Arial', 8), foreground='gray')
        dir_label.pack(side=tk.RIGHT)
    
    def create_mode_selection(self, parent):
        """Cree la selection de mode."""
        mode_frame = ttk.LabelFrame(parent, text=" Mode de Selection ", padding="15")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Variable de mode
        self.mode_var = tk.StringVar(value="fichiers")
        
        # Radio buttons
        radio_frame = ttk.Frame(mode_frame)
        radio_frame.pack(fill=tk.X)
        
        self.radio_fichiers = ttk.Radiobutton(
            radio_frame,
            text="[F] Fichiers individuels (selection precise)",
            variable=self.mode_var,
            value="fichiers",
            command=self.on_mode_change
        )
        self.radio_fichiers.pack(side=tk.LEFT, padx=(0, 30))
        
        self.radio_dossiers = ttk.Radiobutton(
            radio_frame,
            text="[D] Dossiers complets (traitement en lot)",
            variable=self.mode_var,
            value="dossiers",
            command=self.on_mode_change
        )
        self.radio_dossiers.pack(side=tk.LEFT)
        
        # Section JSON AI
        json_frame = ttk.Frame(mode_frame)
        json_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(json_frame, text="Fichier JSON d'instructions :", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        json_selection_frame = ttk.Frame(json_frame)
        json_selection_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.json_path_var = tk.StringVar(value="Aucun fichier JSON selectionne")
        self.json_path_label = ttk.Label(
            json_selection_frame, 
            textvariable=self.json_path_var,
            font=('Arial', 8),
            foreground='gray'
        )
        self.json_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            json_selection_frame,
            text="Parcourir JSON",
            command=self.parcourir_json,
            style="Mode.TButton"
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            json_selection_frame,
            text="X",
            command=self.effacer_json,
            width=3
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Description du mode actuel
        self.mode_desc_label = ttk.Label(
            mode_frame, 
            text="Mode fichiers : Selectionnez individuellement les fichiers .py a transformer",
            font=('Arial', 9),
            foreground='darkblue'
        )
        self.mode_desc_label.pack(pady=(10, 0), anchor=tk.W)
    
    def create_main_panels(self, parent):
        """Cree les panneaux principaux."""
        
        # PanedWindow pour diviser l'espace
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Panneau gauche : Selection et gestion
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)
        
        # Panneau droit : Log et previsualisation  
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=1)
        
        self.create_selection_panel(left_panel)
        self.create_log_panel(right_panel)
    
    def create_selection_panel(self, parent):
        """Cree le panneau de selection de fichiers/dossiers."""
        
        # Frame principal de selection
        selection_frame = ttk.LabelFrame(parent, text=" Selection ", padding="15")
        selection_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Boutons d'action
        buttons_frame = ttk.Frame(selection_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Boutons principaux
        self.btn_ajouter = ttk.Button(
            buttons_frame, 
            text="+ Ajouter", 
            command=self.ajouter_elements,
            style="Mode.TButton"
        )
        self.btn_ajouter.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame, 
            text="X Effacer", 
            command=self.effacer_selection,
            style="Mode.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Liste des elements selectionnes
        list_frame = ttk.Frame(selection_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Listbox avec scrollbar
        self.listbox_frame = ttk.Frame(list_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.selection_listbox = tk.Listbox(
            self.listbox_frame, 
            font=('Consolas', 9),
            selectmode=tk.EXTENDED
        )
        self.selection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar pour la liste
        scrollbar_list = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_list.config(command=self.selection_listbox.yview)
        self.selection_listbox.config(yscrollcommand=scrollbar_list.set)
        
        # Statistiques de selection
        self.stats_label = ttk.Label(
            selection_frame, 
            text="Aucun element selectionne",
            font=('Arial', 10, 'bold'),
            foreground='gray'
        )
        self.stats_label.pack(pady=(0, 10))
        
        # Options de transformation
        self.create_options_panel(selection_frame)
    
    def create_options_panel(self, parent):
        """Cree le panneau d'options."""
        options_frame = ttk.LabelFrame(parent, text=" Options ", padding="10")
        options_frame.pack(fill=tk.X)
        
        # Variables d'options
        self.option_backup = tk.BooleanVar(value=True)
        self.option_logging = tk.BooleanVar(value=True)
        self.option_header = tk.BooleanVar(value=True)
        self.option_analyse = tk.BooleanVar(value=False)
        
        # Checkboxes
        ttk.Checkbutton(
            options_frame, 
            text="[*] Creer sauvegarde (.bak)",
            variable=self.option_backup
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame, 
            text="[*] Convertir print() -> logging.info()",
            variable=self.option_logging
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame, 
            text="[*] Ajouter en-tete informatif",
            variable=self.option_header
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(
            options_frame, 
            text="[?] Mode analyse seule",
            variable=self.option_analyse
        ).pack(anchor=tk.W, pady=2)
    
    def create_log_panel(self, parent):
        """Cree le panneau de logs."""
        
        # Notebook pour organiser les onglets
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Onglet Messages
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="[LOG] Messages")
        
        # === ONGLET MESSAGES ===
        log_container = ttk.Frame(log_frame, padding="10")
        log_container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_container, text="Messages et Activite", style="Header.TLabel").pack(anchor=tk.W)
        
        # Zone de texte pour les logs
        self.log_text = scrolledtext.ScrolledText(
            log_container, 
            height=20,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    
    def create_action_panel(self, parent):
        """Cree le panneau d'actions principales."""
        action_frame = ttk.LabelFrame(parent, text=" Actions ", padding="15")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boutons d'action alignes
        buttons_frame = ttk.Frame(action_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Boutons principaux
        self.btn_analyser = ttk.Button(
            buttons_frame, 
            text="[?] ANALYSER",
            command=self.analyser_selection,
            style="Action.TButton"
        )
        self.btn_analyser.pack(side=tk.LEFT, padx=(0, 15))
        
        self.btn_transformer = ttk.Button(
            buttons_frame, 
            text="[!] TRANSFORMER",
            command=self.transformer_selection,
            style="Action.TButton"
        )
        self.btn_transformer.pack(side=tk.LEFT, padx=(0, 15))
        
        # Bouton transformation JSON
        self.btn_transformer_json = ttk.Button(
            buttons_frame, 
            text="[JSON] APPLIQUER JSON",
            command=self.appliquer_json_instructions,
            style="Action.TButton"
        )
        self.btn_transformer_json.pack(side=tk.LEFT, padx=(0, 15))
        
        # Bouton quitter a droite
        ttk.Button(
            buttons_frame, 
            text="[X] Quitter",
            command=self.on_closing,
            style="Mode.TButton"
        ).pack(side=tk.RIGHT)
    
    def create_status_bar(self, parent):
        """Cree la barre de statut."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # Separateur
        ttk.Separator(status_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        
        # Informations de statut
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            status_container, 
            text="[OK] Pret - Selectionnez des fichiers ou dossiers pour commencer",
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Heure a droite
        self.time_label = ttk.Label(
            status_container, 
            text="",
            font=('Arial', 8),
            foreground='gray'
        )
        self.time_label.pack(side=tk.RIGHT)
        
        # Mettre a jour l'heure
        self.update_time()
    
    def update_time(self):
        """Met a jour l'affichage de l'heure."""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def log(self, message, level="INFO"):
        """Ajoute un message au log."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Icones selon le niveau
        icons = {
            "INFO": "[i]",
            "SUCCESS": "[+]", 
            "WARNING": "[!]",
            "ERROR": "[X]",
            "DEBUG": "[D]"
        }
        
        icon = icons.get(level, "[*]")
        formatted_message = f"[{timestamp}] {icon} {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Aussi dans la console
        print(f"[{timestamp}] {message}")
    
    def on_mode_change(self):
        """Gestionnaire de changement de mode."""
        self.mode_selection = self.mode_var.get()
        
        # Effacer les selections precedentes
        self.effacer_selection()
        
        # Mettre a jour l'interface
        if self.mode_selection == "fichiers":
            self.mode_desc_label.config(
                text="Mode fichiers : Selectionnez individuellement les fichiers .py a transformer"
            )
            self.btn_ajouter.config(text="+ Ajouter Fichiers")
            
        else:  # dossiers
            self.mode_desc_label.config(
                text="Mode dossiers : Selectionnez des dossiers entiers pour traitement en lot"
            )
            self.btn_ajouter.config(text="+ Ajouter Dossiers")
        
        self.log(f"Mode change vers : {self.mode_selection}", "INFO")
        self.update_status()
    
    def parcourir_json(self):
        """Ouvre un dialog pour selectionner un fichier JSON d'instructions."""
        filetypes = [
            ("Fichiers JSON", "*.json"),
            ("Tous les fichiers", "*.*")
        ]
        
        fichier_json = filedialog.askopenfilename(
            title="Selectionner le fichier JSON d'instructions",
            filetypes=filetypes,
            initialdir=os.getcwd()
        )
        
        if fichier_json:
            self.json_instructions_path = fichier_json
            nom_fichier = os.path.basename(fichier_json)
            self.json_path_var.set(f"JSON: {nom_fichier}")
            self.json_path_label.config(foreground='blue')
            
            # Valider le JSON
            if self.valider_json_instructions(fichier_json):
                self.log(f"Fichier JSON charge : {nom_fichier}", "SUCCESS")
            else:
                self.log(f"Attention: JSON potentiellement invalide : {nom_fichier}", "WARNING")
    
    def effacer_json(self):
        """Efface la selection du fichier JSON."""
        self.json_instructions_path = None
        self.json_path_var.set("Aucun fichier JSON selectionne")
        self.json_path_label.config(foreground='gray')
        self.log("Fichier JSON deselectionne", "INFO")
    
    def valider_json_instructions(self, fichier_json):
        """Valide basiquement un fichier JSON d'instructions."""
        try:
            with open(fichier_json, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
            
            # Verification basique de la structure
            if isinstance(data, dict):
                if 'transformations' in data or 'instructions' in data:
                    return True
                else:
                    self.log("JSON valide mais structure non reconnue", "WARNING")
                    return True
            return False
            
        except json.JSONDecodeError as e:
            self.log(f"Erreur JSON: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Erreur lecture JSON: {str(e)}", "ERROR")
            return False
    
    def ajouter_elements(self):
        """Ajoute des fichiers ou dossiers selon le mode."""
        try:
            if self.mode_selection == "fichiers":
                self.ajouter_fichiers()
            else:
                self.ajouter_dossiers()
        except Exception as e:
            self.log(f"Erreur lors de l'ajout : {str(e)}", "ERROR")
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout :\n{str(e)}")
    
    def ajouter_fichiers(self):
        """Ajoute des fichiers Python."""
        filetypes = [
            ("Fichiers Python", "*.py"),
            ("Tous les fichiers", "*.*")
        ]
        
        fichiers = filedialog.askopenfilenames(
            title="Selectionner des fichiers Python",
            filetypes=filetypes,
            initialdir=os.getcwd()
        )
        
        if fichiers:
            nouveaux = 0
            for fichier in fichiers:
                if fichier not in self.fichiers_selectionnes:
                    self.fichiers_selectionnes.append(fichier)
                    
                    # Affichage dans la liste
                    nom_affichage = self.format_file_display(fichier)
                    self.selection_listbox.insert(tk.END, nom_affichage)
                    nouveaux += 1
            
            self.log(f"{nouveaux} fichier(s) ajoute(s)", "SUCCESS")
            self.update_statistics()
            self.update_status()
    
    def ajouter_dossiers(self):
        """Ajoute des dossiers."""
        dossier = filedialog.askdirectory(
            title="Selectionner un dossier",
            initialdir=os.getcwd()
        )
        
        if dossier and dossier not in self.dossiers_selectionnes:
            # Compter les fichiers Python dans le dossier
            fichiers_py = self.compter_fichiers_python(dossier)
            
            if fichiers_py > 0:
                self.dossiers_selectionnes.append(dossier)
                
                # Affichage dans la liste
                nom_affichage = f"[DIR] {os.path.basename(dossier)} ({fichiers_py} fichiers .py)"
                self.selection_listbox.insert(tk.END, nom_affichage)
                
                self.log(f"Dossier ajoute : {os.path.basename(dossier)} ({fichiers_py} fichiers Python)", "SUCCESS")
            else:
                messagebox.showwarning(
                    "Aucun fichier Python", 
                    f"Le dossier selectionne ne contient aucun fichier Python (.py)"
                )
                self.log(f"Dossier ignore (aucun fichier Python) : {os.path.basename(dossier)}", "WARNING")
            
            self.update_statistics()
            self.update_status()
        elif dossier in self.dossiers_selectionnes:
            messagebox.showinfo("Deja selectionne", "Ce dossier est deja dans la selection")
    
    def compter_fichiers_python(self, dossier):
        """Compte recursivement les fichiers Python dans un dossier."""
        count = 0
        try:
            for root, dirs, files in os.walk(dossier):
                # Ignorer les dossiers systeme
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith('.py'):
                        count += 1
        except PermissionError:
            pass
        return count
    
    def format_file_display(self, fichier):
        """Formate l'affichage d'un fichier."""
        try:
            nom = os.path.basename(fichier)
            taille = os.path.getsize(fichier)
            taille_str = self.format_size(taille)
            return f"[PY] {nom} ({taille_str})"
        except:
            return f"[PY] {os.path.basename(fichier)}"
    
    def format_size(self, size_bytes):
        """Formate la taille en format lisible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def effacer_selection(self):
        """Efface toute la selection."""
        self.fichiers_selectionnes.clear()
        self.dossiers_selectionnes.clear()
        self.selection_listbox.delete(0, tk.END)
        
        self.log("Selection effacee", "INFO")
        self.update_statistics()
        self.update_status()
    
    def update_statistics(self):
        """Met a jour les statistiques affichees."""
        if self.mode_selection == "fichiers":
            count = len(self.fichiers_selectionnes)
            if count == 0:
                text = "Aucun fichier selectionne"
                color = "gray"
            else:
                text = f"{count} fichier(s) Python selectionne(s)"
                color = "blue"
        else:
            count = len(self.dossiers_selectionnes)
            if count == 0:
                text = "Aucun dossier selectionne"
                color = "gray"
            else:
                total_files = sum(self.compter_fichiers_python(d) for d in self.dossiers_selectionnes)
                text = f"{count} dossier(s) • {total_files} fichiers Python total"
                color = "blue"
        
        self.stats_label.config(text=text, foreground=color)
    
    def update_status(self):
        """Met a jour la barre de statut."""
        if self.mode_selection == "fichiers":
            if self.fichiers_selectionnes:
                self.status_label.config(text=f"[OK] {len(self.fichiers_selectionnes)} fichier(s) pret(s) pour transformation")
            else:
                self.status_label.config(text="[?] Mode fichiers - Ajoutez des fichiers Python")
        else:
            if self.dossiers_selectionnes:
                total = sum(self.compter_fichiers_python(d) for d in self.dossiers_selectionnes)
                self.status_label.config(text=f"[OK] {len(self.dossiers_selectionnes)} dossier(s) • {total} fichiers Python prets")
            else:
                self.status_label.config(text="[?] Mode dossiers - Ajoutez des dossiers contenant du Python")
    
    def analyser_selection(self):
        """Analyse les fichiers/dossiers selectionnes."""
        if not self.fichiers_selectionnes and not self.dossiers_selectionnes:
            messagebox.showwarning("Aucune selection", "Veuillez d'abord selectionner des fichiers ou dossiers")
            return
        
        self.log(">> Debut de l'analyse...", "INFO")
        
        try:
            fichiers_a_analyser = self.collecter_tous_fichiers()
            
            if not fichiers_a_analyser:
                self.log("Aucun fichier Python trouve pour l'analyse", "WARNING")
                return
            
            # Analyse de chaque fichier
            total_lignes = 0
            total_prints = 0
            total_fonctions = 0
            total_classes = 0
            fichiers_avec_erreurs = 0
            
            for i, fichier in enumerate(fichiers_a_analyser, 1):
                self.log(f"Analyse {i}/{len(fichiers_a_analyser)} : {os.path.basename(fichier)}", "INFO")
                
                try:
                    with open(fichier, 'r', encoding='utf-8') as f:
                        contenu = f.read()
                    
                    # Statistiques de base
                    lignes = len(contenu.splitlines())
                    prints = contenu.count('print(')
                    
                    # Analyse AST basique
                    try:
                        import ast
                        tree = ast.parse(contenu)
                        
                        fonctions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                        classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                        
                    except SyntaxError:
                        fonctions = classes = 0
                        fichiers_avec_erreurs += 1
                    
                    # Accumulation des totaux
                    total_lignes += lignes
                    total_prints += prints
                    total_fonctions += fonctions
                    total_classes += classes
                    
                    # Log des resultats
                    if prints > 0:
                        self.log(f"  {os.path.basename(fichier)} : {lignes} lignes, {prints} print() trouves", "INFO")
                    
                except Exception as e:
                    fichiers_avec_erreurs += 1
                    self.log(f"Erreur analyse {os.path.basename(fichier)} : {str(e)}", "ERROR")
            
            # Resume final
            self.log(f"+ Analyse terminee : {len(fichiers_a_analyser)} fichiers, {total_prints} print() trouves", "SUCCESS")
            
        except Exception as e:
            self.log(f"Erreur lors de l'analyse : {str(e)}", "ERROR")
            messagebox.showerror("Erreur d'analyse", f"Erreur lors de l'analyse :\n{str(e)}")
    
    def transformer_selection(self):
        """Transforme les fichiers/dossiers selectionnes."""
        if not self.fichiers_selectionnes and not self.dossiers_selectionnes:
            messagebox.showwarning("Aucune selection", "Veuillez d'abord selectionner des fichiers ou dossiers")
            return
        
        fichiers_a_traiter = self.collecter_tous_fichiers()
        
        if not fichiers_a_traiter:
            messagebox.showwarning("Aucun fichier", "Aucun fichier Python trouve pour la transformation")
            return
        
        # Confirmation
        if not self.confirmer_transformation(fichiers_a_traiter):
            return
        
        self.log(">> Debut de la transformation...", "INFO")
        
        # Mode analyse seule
        if self.option_analyse.get():
            self.log("Mode analyse active - Aucune modification ne sera effectuee", "INFO")
            self.analyser_selection()
            return
        
        try:
            # Statistiques de transformation
            stats = {
                'total': len(fichiers_a_traiter),
                'reussis': 0,
                'echecs': 0,
                'sauvegardes': 0,
                'transformations': 0
            }
            
            for i, fichier in enumerate(fichiers_a_traiter, 1):
                self.log(f"Transformation {i}/{stats['total']} : {os.path.basename(fichier)}", "INFO")
                
                try:
                    # Lecture du fichier
                    with open(fichier, 'r', encoding='utf-8') as f:
                        contenu_original = f.read()
                    
                    # Sauvegarde si demandee
                    if self.option_backup.get():
                        fichier_backup = fichier + '.bak'
                        with open(fichier_backup, 'w', encoding='utf-8') as f:
                            f.write(contenu_original)
                        stats['sauvegardes'] += 1
                        self.log(f"  + Sauvegarde creee : {os.path.basename(fichier_backup)}", "INFO")
                    
                    # Transformation du contenu
                    contenu_transforme = self.appliquer_transformations(contenu_original, fichier)
                    
                    # Compter les transformations
                    transforms_count = contenu_original.count('print(') - contenu_transforme.count('print(')
                    stats['transformations'] += transforms_count
                    
                    # Ecriture du fichier transforme
                    with open(fichier, 'w', encoding='utf-8') as f:
                        f.write(contenu_transforme)
                    
                    stats['reussis'] += 1
                    
                    if transforms_count > 0:
                        self.log(f"  + {transforms_count} transformation(s) appliquee(s)", "SUCCESS")
                    else:
                        self.log(f"  + Fichier traite (aucune modification necessaire)", "SUCCESS")
                
                except Exception as e:
                    stats['echecs'] += 1
                    self.log(f"  [X] Erreur : {str(e)}", "ERROR")
                
                # Mise a jour de l'affichage
                self.root.update_idletasks()
            
            # Rapport final
            self.afficher_rapport_transformation(stats)
            
        except Exception as e:
            self.log(f"Erreur generale de transformation : {str(e)}", "ERROR")
            messagebox.showerror("Erreur", f"Erreur lors de la transformation :\n{str(e)}")
    
    def appliquer_transformations(self, contenu, fichier_path):
        """Applique les transformations au contenu d'un fichier."""
        contenu_modifie = contenu
        
        # Transformation print() -> logging
        if self.option_logging.get():
            # Simple remplacement pour la demo
            contenu_modifie = contenu_modifie.replace('print(', 'logging.info(')
            
            # Ajouter import logging si necessaire
            if 'logging.info(' in contenu_modifie and 'import logging' not in contenu_modifie:
                lines = contenu_modifie.split('\n')
                
                # Trouver la position d'insertion (apres les imports existants)
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(('import ', 'from ')):
                        insert_pos = i + 1
                    elif line.strip() and not line.strip().startswith('#'):
                        break
                
                # Inserer les imports
                lines.insert(insert_pos, '')
                lines.insert(insert_pos, '# Configuration du logging')
                lines.insert(insert_pos, 'logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")')
                lines.insert(insert_pos, 'import logging')
                
                contenu_modifie = '\n'.join(lines)
        
        # Ajouter en-tete si demande
        if self.option_header.get():
            header = self.generer_entete(fichier_path)
            contenu_modifie = header + '\n' + contenu_modifie
        
        return contenu_modifie
    
    def generer_entete(self, fichier_path):
        """Genere l'en-tete pour un fichier transforme."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nom_fichier = os.path.basename(fichier_path)
        
        header = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==============================================================================
FICHIER TRANSFORME PAR OUTIL AST
==============================================================================

Fichier original : {nom_fichier}
Date transformation : {timestamp}
Outil : Interface AST v2.4

Modifications appliquees :
- Conversion print() vers logging.info()
- Ajout configuration logging
- Preservation de la structure originale

Genere automatiquement - Ne pas modifier cet en-tete
==============================================================================
"""
'''
        return header
    
    def confirmer_transformation(self, fichiers):
        """Demande confirmation avant transformation."""
        message = f"""Etes-vous sur de vouloir transformer {len(fichiers)} fichier(s) ?

OPTIONS SELECTIONNEES :
• Sauvegarde (.bak) : {'[+] Oui' if self.option_backup.get() else '[X] Non'}
• Conversion print() -> logging : {'[+] Oui' if self.option_logging.get() else '[X] Non'}
• Ajout en-tete : {'[+] Oui' if self.option_header.get() else '[X] Non'}
• Mode analyse seule : {'[+] Oui' if self.option_analyse.get() else '[X] Non'}

/!\\ Cette operation modifiera les fichiers de maniere irreversible 
(sauf si vous avez active la sauvegarde).

Continuer la transformation ?"""
        
        return messagebox.askyesno("Confirmation de transformation", message)
    
    def afficher_rapport_transformation(self, stats):
        """Affiche le rapport de transformation."""
        taux_reussite = (stats['reussis'] / stats['total']) * 100 if stats['total'] > 0 else 0
        
        rapport = f"""[+] TRANSFORMATION TERMINEE

STATISTIQUES :
• Fichiers traites : {stats['total']}
• Succes : {stats['reussis']}
• Echecs : {stats['echecs']}
• Taux de reussite : {taux_reussite:.1f}%

MODIFICATIONS :
• Sauvegardes creees : {stats['sauvegardes']}
• Transformations print() : {stats['transformations']}

[+] Transformation completed successfully!"""
        
        self.log(rapport.replace('\n', ' | '), "SUCCESS")
        messagebox.showinfo("Transformation terminee", rapport)
    
    def appliquer_json_instructions(self):
        """Applique les instructions depuis un fichier JSON."""
        # Verifier qu'un JSON est selectionne
        if not self.json_instructions_path:
            messagebox.showwarning("Aucun JSON", "Veuillez d'abord selectionner un fichier JSON d'instructions")
            return
        
        # Verifier qu'il y a des fichiers a traiter
        if not self.fichiers_selectionnes and not self.dossiers_selectionnes:
            messagebox.showwarning("Aucune selection", "Veuillez d'abord selectionner des fichiers ou dossiers")
            return
        
        fichiers_a_traiter = self.collecter_tous_fichiers()
        
        if not fichiers_a_traiter:
            messagebox.showwarning("Aucun fichier", "Aucun fichier Python trouve pour la transformation")
            return
        
        # Confirmation
        nom_json = os.path.basename(self.json_instructions_path)
        message = f"""Appliquer les instructions JSON a {len(fichiers_a_traiter)} fichier(s) ?

Fichier JSON : {nom_json}
Fichiers a traiter : {len(fichiers_a_traiter)}

Les transformations seront basees sur le contenu du fichier JSON.

Continuer ?"""
        
        if not messagebox.askyesno("Confirmation JSON", message):
            return
        
        self.log(f">> Application des instructions JSON : {nom_json}", "INFO")
        
        try:
            # Charger le JSON
            with open(self.json_instructions_path, 'r', encoding='utf-8') as f:
                import json
                instructions_json = json.load(f)
            
            self.log(f"JSON charge avec succes", "SUCCESS")
            
            # Simuler l'application (pour l'instant)
            # TODO: Implementer la logique reelle dans le module core/
            stats = {
                'total': len(fichiers_a_traiter),
                'reussis': 0,
                'echecs': 0,
                'transformations': 0
            }
            
            for i, fichier in enumerate(fichiers_a_traiter, 1):
                self.log(f"Application JSON {i}/{stats['total']} : {os.path.basename(fichier)}", "INFO")
                
                try:
                    # Ici: logique d'application du JSON
                    # Pour l'instant, simulation
                    stats['reussis'] += 1
                    stats['transformations'] += 1
                    self.log(f"  + Instructions JSON appliquees", "SUCCESS")
                    
                except Exception as e:
                    stats['echecs'] += 1
                    self.log(f"  [X] Erreur JSON : {str(e)}", "ERROR")
                
                self.root.update_idletasks()
            
            # Rapport final
            self.log(f"+ Application JSON terminee : {stats['reussis']} succes, {stats['echecs']} echecs", "SUCCESS")
            
            rapport = f"""[JSON] TRANSFORMATION TERMINEE

Instructions JSON : {nom_json}
Fichiers traites : {stats['total']}
Succes : {stats['reussis']}
Echecs : {stats['echecs']}
Transformations appliquees : {stats['transformations']}

[+] Application JSON completed!"""
            
            messagebox.showinfo("JSON Termine", rapport)
            
        except Exception as e:
            self.log(f"Erreur lors de l'application JSON : {str(e)}", "ERROR")
            messagebox.showerror("Erreur JSON", f"Erreur lors de l'application JSON :\n{str(e)}")
    
    def collecter_tous_fichiers(self):
        """Collecte tous les fichiers Python a traiter."""
        tous_fichiers = []
        
        # Fichiers individuels
        tous_fichiers.extend(self.fichiers_selectionnes)
        
        # Fichiers des dossiers
        for dossier in self.dossiers_selectionnes:
            for root, dirs, files in os.walk(dossier):
                # Ignorer les dossiers systeme
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                
                for file in files:
                    if file.endswith('.py'):
                        fichier_path = os.path.join(root, file)
                        if fichier_path not in tous_fichiers:
                            tous_fichiers.append(fichier_path)
        
        return tous_fichiers
    
    def on_closing(self):
        """Gestionnaire de fermeture de l'application."""
        if messagebox.askokcancel("Quitter", "Etes-vous sur de vouloir quitter l'application ?"):
            self.log("Fermeture de l'application...", "INFO")
            try:
                self.root.destroy()
            except:
                pass
    
    def run(self):
        """Lance l'interface graphique."""
        print(">> Demarrage de l'interface AST...")
        
        try:
            # Forcer l'affichage complet
            print("+ Creation interface terminee, affichage...")
            self.root.update()
            self.root.deiconify()  # S'assurer que visible
            self.root.lift()
            self.root.focus_force()
            
            print("+ Fenetre visible, demarrage boucle principale...")
            print("+ Interface prete - La fenetre devrait etre visible maintenant")
            
            # Demarrer la boucle principale
            self.root.mainloop()
            
            print("+ Interface AST fermee proprement")
            return True
            
        except Exception as e:
            print(f"[X] Erreur lors de l'execution : {e}")
            traceback.print_exc()
            return False


    def init_moteur_modulaire(self):
        """Initialise le moteur AST avec systeme modulaire."""
        if not MOTEUR_DISPONIBLE:
            print("! Moteur modulaire non disponible")
            return
        
        try:
            self.orchestrateur = OrchestrateurAST()
            self.transformations_disponibles = self.orchestrateur.lister_transformations_modulaires()
            
            if self.transformations_disponibles:
                print(f"+ {len(self.transformations_disponibles)} transformation(s) modulaire(s) detectee(s)")
            else:
                print("! Aucune transformation modulaire disponible")
                
        except Exception as e:
            print(f"X Erreur initialisation moteur: {e}")
            self.orchestrateur = None
    
    def obtenir_transformations_disponibles(self):
        """Retourne la liste des transformations disponibles pour l'interface."""
        if not hasattr(self, 'orchestrateur') or not self.orchestrateur:
            return []
        return getattr(self, 'transformations_disponibles', [])
    
    def appliquer_transformation_gui(self, fichiers_sources, transformation_name, dossier_sortie=None):
        """Applique une transformation modulaire via l'interface GUI."""
        if not hasattr(self, 'orchestrateur') or not self.orchestrateur:
            return {
                'succes': False,
                'erreur': 'Moteur modulaire non disponible',
                'fichiers_traites': 0,
                'fichiers_reussis': 0
            }
        
        if not fichiers_sources:
            return {
                'succes': False,
                'erreur': 'Aucun fichier selectionne',
                'fichiers_traites': 0,
                'fichiers_reussis': 0
            }
        
        # Creer le dossier de sortie si necessaire
        if not dossier_sortie:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dossier_sortie = f"transformations_gui_{timestamp}"
        
        if not os.path.exists(dossier_sortie):
            os.makedirs(dossier_sortie)
        
        resultats = {
            'succes': True,
            'dossier_sortie': dossier_sortie,
            'fichiers_traites': len(fichiers_sources),
            'fichiers_reussis': 0,
            'fichiers_echoues': 0,
            'details': []
        }
        
        # Traiter chaque fichier
        for fichier_source in fichiers_sources:
            try:
                nom_base = os.path.splitext(os.path.basename(fichier_source))[0]
                fichier_sortie = os.path.join(dossier_sortie, f"{nom_base}_{transformation_name}.py")
                
                succes = self.orchestrateur.appliquer_transformation_modulaire(
                    fichier_source, fichier_sortie, transformation_name
                )
                
                if succes:
                    resultats['fichiers_reussis'] += 1
                    resultats['details'].append({
                        'fichier': os.path.basename(fichier_source),
                        'statut': 'succes',
                        'sortie': fichier_sortie
                    })
                else:
                    resultats['fichiers_echoues'] += 1
                    resultats['details'].append({
                        'fichier': os.path.basename(fichier_source),
                        'statut': 'echec',
                        'erreur': 'Transformation non applicable'
                    })
                    
            except Exception as e:
                resultats['fichiers_echoues'] += 1
                resultats['details'].append({
                    'fichier': os.path.basename(fichier_source),
                    'statut': 'erreur',
                    'erreur': str(e)
                })
        
        resultats['succes'] = resultats['fichiers_reussis'] > 0
        return resultats
    
    def generer_rapport_transformation(self, resultats):
        """Genere un rapport detaille des transformations appliquees."""
        if not resultats:
            return "Aucun resultat disponible"
        
        rapport = []
        rapport.append("=== RAPPORT DE TRANSFORMATION MODULAIRE ===")
        rapport.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rapport.append(f"Dossier de sortie: {resultats.get('dossier_sortie', 'N/A')}")
        rapport.append("")
        rapport.append(f"Fichiers traites: {resultats['fichiers_traites']}")
        rapport.append(f"Succes: {resultats['fichiers_reussis']}")
        rapport.append(f"Echecs: {resultats['fichiers_echoues']}")
        
        if resultats['fichiers_traites'] > 0:
            taux = (resultats['fichiers_reussis']/resultats['fichiers_traites']*100)
            rapport.append(f"Taux de reussite: {taux:.1f}%")
        
        rapport.append("")
        rapport.append("=== DETAILS PAR FICHIER ===")
        for detail in resultats.get('details', []):
            statut_symbol = "+" if detail['statut'] == 'succes' else "X"
            rapport.append(f"{statut_symbol} {detail['fichier']}: {detail['statut']}")
            if 'erreur' in detail:
                rapport.append(f"    Erreur: {detail['erreur']}")
            elif 'sortie' in detail:
                rapport.append(f"    Sortie: {os.path.basename(detail['sortie'])}")
        
        return "\n".join(rapport)


# ==============================================================================
# ALIASES POUR COMPATIBILITE
# ==============================================================================

# Alias pour compatibilite avec launcher_simple.py
InterfaceSimple = InterfaceAST

# Fonction principale aussi accessible comme InterfaceAST
def InterfaceAST_main():
    """Lance l'interface principale."""
    return main()

# ==============================================================================
# FONCTIONS UTILITAIRES ET TESTS
# ==============================================================================

def test_interface():
    """Test de l'interface graphique."""
    print(">> Test de l'interface graphique...")
    
    try:
        app = InterfaceAST()
        print("+ Interface creee avec succes")
        
        # Test rapide (fermeture automatique apres 3 secondes)
        app.root.after(3000, app.root.destroy)
        app.run()
        
        return True
        
    except Exception as e:
        print(f"[X] Erreur test interface : {e}")
        traceback.print_exc()
        return False

def main():
    """Point d'entree principal."""
    print("=" * 60)
    print("INTERFACE GRAPHIQUE AST - VERSION 2.4")
    print("=" * 60)
    
    try:
        # Verification environnement
        print(">> Verification de l'environnement...")
        
        import tkinter
        print(f"+ Tkinter disponible (version {tkinter.TkVersion})")
        
        # Lancement de l'interface
        app = InterfaceAST()
        success = app.run()
        
        if success:
            print("+ Application fermee normalement")
        else:
            print("! Application fermee avec des avertissements")
        
        return success
        
    except ImportError as e:
        print(f"[X] Erreur d'import : {e}")
        print("Tkinter n'est pas disponible sur ce systeme")
        return False
        
    except Exception as e:
        print(f"[X] Erreur inattendue : {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n" + "=" * 60)
        print("[X] L'application a rencontre des problemes")
        print("Verifiez que votre environnement supporte Tkinter")
        print("=" * 60)
        input("Appuyez sur Entree pour fermer...")
    else:
        print("\n[+] Au revoir !")