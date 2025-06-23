#!/usr/bin/env python3
"""
Sélecteur de Fichiers/Dossiers Python - Interface GUI Tkinter Avancée
====================================================================

Module d'interface graphique pour sélectionner :
- Un fichier Python unique (.py)
- Plusieurs dossiers (traitement en lot)

Intégration avec modificateur_interactif.py pour le mode "démonstration".
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from pathlib import Path

class FileSelectorApp:
    """Interface graphique pour sélectionner des fichiers Python ou dossiers."""
    
    def __init__(self, master):
        self.master = master
        self.selected_files = []
        self.selected_folders = []
        self.current_directory = os.getcwd()
        self.selection_mode = "file"  # "file" ou "folders"
        
        # Configuration de la fenêtre principale
        master.title("Sélecteur de Fichiers/Dossiers Python - Outil AST")
        master.geometry("1200x800")
        master.minsize(900, 700)
        
        # Configuration du style
        self.setup_styles()
        
        # Interface utilisateur
        self.create_widgets()
        
        # Initialisation
        self.update_interface_for_mode()
        self.populate_tree()
        
        # Gestion des événements
        master.protocol("WM_DELETE_WINDOW", self.on_closing)
        master.bind("<Escape>", lambda e: self.cancel_selection())
    
    def setup_styles(self):
        """Configure les styles de l'interface."""
        style = ttk.Style()
        
        # Style pour les boutons
        style.configure("Action.TButton", padding=(10, 5))
        style.configure("Cancel.TButton", padding=(10, 5))
        style.configure("Mode.TButton", padding=(8, 4))
    
    def create_widgets(self):
        """Crée l'interface utilisateur complète."""
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre et sélection du mode
        self.create_header_with_mode(main_frame)
        
        # Zone de navigation
        self.create_navigation(main_frame)
        
        # Zone principale divisée en deux panneaux
        self.create_main_panels(main_frame)
        
        # Zone des boutons d'action
        self.create_action_buttons(main_frame)
        
        # Barre de statut
        self.create_status_bar(main_frame)
    
    def create_header_with_mode(self, parent):
        """Crée la zone d'en-tête avec titre et sélection de mode."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Titre
        title_label = ttk.Label(
            header_frame, 
            text="Sélecteur de Fichiers/Dossiers Python", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(side=tk.TOP, anchor=tk.W)
        
        # Frame pour les modes
        mode_frame = ttk.Frame(header_frame)
        mode_frame.pack(side=tk.TOP, anchor=tk.W, pady=(10, 0))
        
        ttk.Label(mode_frame, text="Mode de sélection :", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Radio buttons pour le mode
        self.mode_var = tk.StringVar(value="file")
        
        self.radio_file = ttk.Radiobutton(
            mode_frame,
            text="📄 Fichier unique",
            variable=self.mode_var,
            value="file",
            command=self.on_mode_change
        )
        self.radio_file.pack(side=tk.LEFT, padx=(10, 0))
        
        self.radio_folders = ttk.Radiobutton(
            mode_frame,
            text="📁 Dossiers multiples",
            variable=self.mode_var,
            value="folders",
            command=self.on_mode_change
        )
        self.radio_folders.pack(side=tk.LEFT, padx=(10, 0))
        
        # Informations sur le répertoire actuel
        self.dir_info_label = ttk.Label(
            header_frame, 
            text=f"Répertoire : {self.current_directory}",
            foreground="gray"
        )
        self.dir_info_label.pack(side=tk.TOP, anchor=tk.W, pady=(5, 0))
    
    def create_navigation(self, parent):
        """Crée la zone de navigation avec changement de répertoire."""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Boutons de navigation
        ttk.Button(
            nav_frame, 
            text="↑ Dossier parent", 
            command=self.go_parent_directory,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            nav_frame, 
            text="📁 Changer dossier", 
            command=self.change_directory,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            nav_frame, 
            text="🔄 Actualiser", 
            command=self.refresh_tree,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Bouton spécial pour mode dossiers
        self.select_current_folder_btn = ttk.Button(
            nav_frame, 
            text="➕ Ajouter ce dossier", 
            command=self.add_current_folder,
            style="Mode.TButton"
        )
        self.select_current_folder_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Compteur de fichiers
        self.file_count_label = ttk.Label(nav_frame, text="")
        self.file_count_label.pack(side=tk.RIGHT)
    
    def create_main_panels(self, parent):
        """Crée les panneaux principaux : arborescence et prévisualisation."""
        
        # PanedWindow pour diviser l'espace
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Panneau gauche : Arborescence des fichiers
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Panneau droit : Prévisualisation/Sélection
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        self.create_file_tree(left_frame)
        self.create_selection_panel(right_frame)
    
    def create_file_tree(self, parent):
        """Crée l'arborescence des fichiers."""
        
        # Label dynamique selon le mode
        self.tree_label = ttk.Label(parent, text="", font=("Arial", 10, "bold"))
        self.tree_label.pack(anchor=tk.W)
        
        # Frame pour l'arborescence avec scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Configuration des colonnes
        self.tree["columns"] = ("type", "count", "size")
        self.tree.column("#0", width=250, minwidth=180)
        self.tree.column("type", width=80, minwidth=60)
        self.tree.column("count", width=80, minwidth=60)
        self.tree.column("size", width=80, minwidth=60)
        
        self.tree.heading("#0", text="Nom", anchor=tk.W)
        self.tree.heading("type", text="Type", anchor=tk.CENTER)
        self.tree.heading("count", text="Fichiers .py", anchor=tk.CENTER)
        self.tree.heading("size", text="Taille", anchor=tk.CENTER)
        
        # Événements
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tree.bind("<Double-1>", self.on_double_click)
    
    def create_selection_panel(self, parent):
        """Crée le panneau de prévisualisation/sélection."""
        
        # Notebook pour organiser les onglets
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Onglet 1 : Aperçu
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="📄 Aperçu")
        
        # Onglet 2 : Sélection
        selection_frame = ttk.Frame(self.notebook)
        self.notebook.add(selection_frame, text="✅ Sélection")
        
        self.create_preview_tab(preview_frame)
        self.create_selection_tab(selection_frame)
    
    def create_preview_tab(self, parent):
        """Crée l'onglet d'aperçu."""
        
        # Frame pour le texte avec scrollbars
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de texte
        self.preview_text = tk.Text(
            preview_frame, 
            wrap=tk.NONE, 
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#f8f8f8",
            fg="#333333"
        )
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars pour la prévisualisation
        v_scroll_preview = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        v_scroll_preview.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.configure(yscrollcommand=v_scroll_preview.set)
        
        h_scroll_preview = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.preview_text.xview)
        h_scroll_preview.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_text.configure(xscrollcommand=h_scroll_preview.set)
        
        # Informations sur l'élément sélectionné
        self.item_info_frame = ttk.Frame(parent)
        self.item_info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.item_info_label = ttk.Label(
            self.item_info_frame, 
            text="Aucun élément sélectionné",
            foreground="gray"
        )
        self.item_info_label.pack(anchor=tk.W)
    
    def create_selection_tab(self, parent):
        """Crée l'onglet de gestion des sélections."""
        
        # Frame principal avec padding
        main_selection_frame = ttk.Frame(parent, padding="5")
        main_selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Section mode fichier unique
        self.file_section = ttk.LabelFrame(main_selection_frame, text="Fichier sélectionné", padding="10")
        self.file_section.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_file_label = ttk.Label(self.file_section, text="Aucun fichier sélectionné", foreground="gray")
        self.selected_file_label.pack(anchor=tk.W)
        
        # Section mode dossiers multiples
        self.folders_section = ttk.LabelFrame(main_selection_frame, text="Dossiers sélectionnés", padding="10")
        self.folders_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Liste des dossiers sélectionnés
        folders_list_frame = ttk.Frame(self.folders_section)
        folders_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox avec scrollbar
        listbox_frame = ttk.Frame(folders_list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.folders_listbox = tk.Listbox(listbox_frame, font=("Arial", 9))
        self.folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        folders_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.folders_listbox.yview)
        folders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.folders_listbox.configure(yscrollcommand=folders_scrollbar.set)
        
        # Boutons de gestion des dossiers
        folders_buttons_frame = ttk.Frame(self.folders_section)
        folders_buttons_frame.pack(fill=tk.X)
        
        ttk.Button(
            folders_buttons_frame, 
            text="➕ Ajouter dossier", 
            command=self.add_folder_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            folders_buttons_frame, 
            text="❌ Supprimer", 
            command=self.remove_selected_folder
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            folders_buttons_frame, 
            text="🗑️ Vider tout", 
            command=self.clear_all_folders
        ).pack(side=tk.LEFT)
        
        # Statistiques des dossiers
        self.folders_stats_label = ttk.Label(
            self.folders_section, 
            text="Aucun dossier sélectionné",
            foreground="blue"
        )
        self.folders_stats_label.pack(anchor=tk.W, pady=(10, 0))
    
    def create_action_buttons(self, parent):
        """Crée les boutons d'action."""
        
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Bouton Annuler
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Annuler", 
            command=self.cancel_selection,
            style="Cancel.TButton"
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Bouton Sélectionner
        self.select_button = ttk.Button(
            button_frame, 
            text="Sélectionner", 
            command=self.confirm_selection,
            style="Action.TButton",
            state=tk.DISABLED
        )
        self.select_button.pack(side=tk.RIGHT)
        
        # Bouton aide
        help_button = ttk.Button(
            button_frame, 
            text="? Aide", 
            command=self.show_help,
            width=8
        )
        help_button.pack(side=tk.LEFT)
    
    def create_status_bar(self, parent):
        """Crée la barre de statut."""
        
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Séparateur
        ttk.Separator(status_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Prêt - Sélectionnez le mode et les éléments",
            foreground="blue"
        )
        self.status_label.pack(side=tk.LEFT)
    
    def on_mode_change(self):
        """Gestionnaire de changement de mode."""
        self.selection_mode = self.mode_var.get()
        
        # Réinitialiser les sélections
        self.selected_files = []
        self.selected_folders = []
        
        # Mettre à jour l'interface
        self.update_interface_for_mode()
        self.populate_tree()
        self.update_selection_display()
        self.update_action_button_state()
    
    def update_interface_for_mode(self):
        """Met à jour l'interface selon le mode sélectionné."""
        if self.selection_mode == "file":
            self.tree_label.config(text="Fichiers Python (.py)")
            self.select_current_folder_btn.pack_forget()
            
            # Afficher la section fichier, masquer la section dossiers
            self.file_section.pack(fill=tk.X, pady=(0, 10))
            self.folders_section.pack_forget()
            
            self.status_label.config(text="Mode fichier unique - Sélectionnez un fichier Python")
            
        else:  # folders
            self.tree_label.config(text="Dossiers (avec fichiers Python)")
            self.select_current_folder_btn.pack(side=tk.LEFT, padx=(10, 0))
            
            # Masquer la section fichier, afficher la section dossiers
            self.file_section.pack_forget()
            self.folders_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            self.status_label.config(text="Mode dossiers multiples - Ajoutez des dossiers à traiter")
    
    def populate_tree(self):
        """Remplit l'arborescence selon le mode actuel."""
        
        # Effacer l'arborescence existante
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            items = []
            
            if self.selection_mode == "file":
                # Mode fichier : afficher les fichiers Python et dossiers
                self.populate_tree_file_mode(items)
            else:
                # Mode dossiers : afficher tous les dossiers avec comptage
                self.populate_tree_folder_mode(items)
            
            # Trier les éléments
            items.sort(key=lambda x: (x[0] != "folder", x[1].lower()))
            
            # Ajouter à l'arborescence
            for item_type, name, path, extra_info in items:
                if item_type == "folder":
                    count, size = extra_info
                    icon = "📁" if count > 0 else "📂"
                    self.tree.insert("", "end", 
                                   text=f"{icon} {name}", 
                                   values=("Dossier", count, size), 
                                   tags=("folder",))
                else:
                    size, modified = extra_info
                    self.tree.insert("", "end", 
                                   text=f"🐍 {name}", 
                                   values=("Fichier Python", "", size), 
                                   tags=("file",))
            
            self.update_file_count_display()
            
        except Exception as e:
            self.status_label.config(text=f"Erreur lors du chargement : {str(e)}", foreground="red")
            messagebox.showerror("Erreur", f"Erreur lors du chargement du répertoire :\n{str(e)}")
        
        # Mettre à jour l'affichage du répertoire
        self.dir_info_label.config(text=f"Répertoire : {self.current_directory}")
    
    def populate_tree_file_mode(self, items):
        """Remplit l'arborescence en mode fichier."""
        for item in os.listdir(self.current_directory):
            item_path = os.path.join(self.current_directory, item)
            
            if os.path.isdir(item_path):
                # Compter les fichiers Python dans ce dossier
                py_count = self.count_python_files_recursive(item_path)
                if py_count > 0:
                    size_info = self.get_folder_size_info(item_path)
                    items.append(("folder", item, item_path, (py_count, size_info)))
            
            elif item.endswith('.py'):
                try:
                    stat = os.stat(item_path)
                    size = self.format_size(stat.st_size)
                    modified = self.format_date(stat.st_mtime)
                    items.append(("file", item, item_path, (size, modified)))
                except OSError:
                    items.append(("file", item, item_path, ("", "")))
    
    def populate_tree_folder_mode(self, items):
        """Remplit l'arborescence en mode dossiers."""
        for item in os.listdir(self.current_directory):
            item_path = os.path.join(self.current_directory, item)
            
            if os.path.isdir(item_path):
                # Compter les fichiers Python
                py_count = self.count_python_files_recursive(item_path)
                size_info = self.get_folder_size_info(item_path)
                
                # Afficher tous les dossiers, même ceux sans Python
                items.append(("folder", item, item_path, (py_count, size_info)))
    
    def count_python_files_recursive(self, directory_path, max_depth=3, current_depth=0):
        """Compte récursivement les fichiers Python dans un dossier."""
        if current_depth > max_depth:
            return 0
        
        count = 0
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if os.path.isfile(item_path) and item.endswith('.py'):
                    count += 1
                elif os.path.isdir(item_path) and current_depth < max_depth:
                    count += self.count_python_files_recursive(item_path, max_depth, current_depth + 1)
        except (PermissionError, OSError):
            pass
        
        return count
    
    def get_folder_size_info(self, directory_path):
        """Obtient des informations sur la taille d'un dossier."""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except OSError:
                            pass
                
                # Limiter la profondeur pour éviter les scans trop longs
                if len(root.replace(directory_path, '').split(os.sep)) > 3:
                    dirs.clear()
            
            if total_size > 0:
                return self.format_size(total_size)
            else:
                return ""
        except:
            return ""
    
    def format_size(self, size_bytes):
        """Formate la taille en format lisible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def format_date(self, timestamp):
        """Formate la date de modification."""
        import datetime
        return datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y")
    
    def update_file_count_display(self):
        """Met à jour l'affichage du compteur de fichiers."""
        if self.selection_mode == "file":
            py_files = len([item for item in self.tree.get_children() 
                           if self.tree.item(item, "text").startswith("🐍")])
            folders = len([item for item in self.tree.get_children() 
                          if self.tree.item(item, "text").startswith("📁")])
            self.file_count_label.config(text=f"{py_files} fichiers Python, {folders} dossiers")
        else:
            folders = len(self.tree.get_children())
            total_py = sum(int(self.tree.item(item, "values")[1] or 0) 
                          for item in self.tree.get_children())
            self.file_count_label.config(text=f"{folders} dossiers, {total_py} fichiers Python total")
    
    def on_item_select(self, event):
        """Gestionnaire de sélection d'élément."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = self.tree.item(item, "text")
        item_values = self.tree.item(item, "values")
        
        if self.selection_mode == "file":
            if item_text.startswith("🐍"):
                # Fichier Python sélectionné
                filename = item_text[2:]
                file_path = os.path.join(self.current_directory, filename)
                
                if os.path.exists(file_path):
                    self.selected_files = [file_path]
                    self.preview_file(file_path)
                    self.update_selection_display()
                    self.update_action_button_state()
                    
                    # Informations du fichier
                    size = item_values[2] if len(item_values) > 2 else ""
                    self.item_info_label.config(text=f"Fichier : {filename} | Taille : {size}")
                    self.status_label.config(text=f"Fichier sélectionné : {filename}", foreground="blue")
            
            elif item_text.startswith("📁"):
                # Dossier sélectionné en mode fichier
                self.selected_files = []
                self.preview_folder_info(item_text[2:], item_values)
                self.update_selection_display()
                self.update_action_button_state()
        
        else:  # mode folders
            if item_text.startswith(("📁", "📂")):
                folder_name = item_text[2:]
                py_count = item_values[1] if len(item_values) > 1 else "0"
                size = item_values[2] if len(item_values) > 2 else ""
                
                self.item_info_label.config(
                    text=f"Dossier : {folder_name} | {py_count} fichiers Python | {size}"
                )
                
                self.preview_folder_info(folder_name, item_values)
    
    def preview_file(self, file_path):
        """Affiche l'aperçu d'un fichier."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Limiter l'aperçu à 100 lignes
            preview_lines = lines[:100]
            
            # En-tête
            self.preview_text.insert(tk.END, f"# Aperçu : {os.path.basename(file_path)} ({len(lines)} lignes)\n")
            self.preview_text.insert(tk.END, f"# {'=' * 50}\n\n")
            
            # Contenu avec numérotation
            for i, line in enumerate(preview_lines, 1):
                self.preview_text.insert(tk.END, f"{i:3d} | {line}")
            
            if len(lines) > 100:
                self.preview_text.insert(tk.END, f"\n... ({len(lines) - 100} lignes supplémentaires)")
            
        except UnicodeDecodeError:
            self.preview_text.insert(tk.END, "Erreur : Impossible de décoder le fichier (encodage non supporté)")
        except Exception as e:
            self.preview_text.insert(tk.END, f"Erreur lors de la lecture du fichier :\n{str(e)}")
        
        self.preview_text.config(state=tk.DISABLED)
    
    def preview_folder_info(self, folder_name, values):
        """Affiche les informations d'un dossier."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        folder_path = os.path.join(self.current_directory, folder_name)
        
        self.preview_text.insert(tk.END, f"# Informations du dossier : {folder_name}\n")
        self.preview_text.insert(tk.END, f"# {'=' * 50}\n\n")
        
        if os.path.exists(folder_path):
            try:
                # Lister les fichiers Python
                python_files = []
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if file.endswith('.py'):
                            rel_path = os.path.relpath(os.path.join(root, file), folder_path)
                            python_files.append(rel_path)
                    
                    # Limiter la profondeur
                    if len(root.replace(folder_path, '').split(os.sep)) > 2:
                        dirs.clear()
                
                self.preview_text.insert(tk.END, f"Chemin complet : {folder_path}\n")
                self.preview_text.insert(tk.END, f"Fichiers Python trouvés : {len(python_files)}\n\n")
                
                if python_files:
                    self.preview_text.insert(tk.END, "Fichiers Python dans ce dossier :\n")
                    self.preview_text.insert(tk.END, "-" * 40 + "\n")
                    
                    for i, py_file in enumerate(python_files[:20], 1):
                        self.preview_text.insert(tk.END, f"{i:2d}. {py_file}\n")
                    
                    if len(python_files) > 20:
                        self.preview_text.insert(tk.END, f"... et {len(python_files) - 20} autres fichiers\n")
                else:
                    self.preview_text.insert(tk.END, "Aucun fichier Python trouvé dans ce dossier.\n")
                
            except Exception as e:
                self.preview_text.insert(tk.END, f"Erreur lors de l'analyse du dossier :\n{str(e)}")
        else:
            self.preview_text.insert(tk.END, "Dossier non accessible ou inexistant.")
        
        self.preview_text.config(state=tk.DISABLED)
    
    def on_double_click(self, event):
        """Gestionnaire de double-clic."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = self.tree.item(item, "text")
        
        if item_text.startswith(("📁", "📂")):
            # Entrer dans le dossier
            folder_name = item_text[2:]
            new_path = os.path.join(self.current_directory, folder_name)
            
            if os.path.isdir(new_path):
                self.current_directory = new_path
                self.populate_tree()
        
        elif item_text.startswith("🐍") and self.selection_mode == "file":
            # Sélectionner le fichier directement
            self.confirm_selection()
    
    def add_current_folder(self):
        """Ajoute le dossier actuel à la sélection (mode dossiers)."""
        if self.selection_mode != "folders":
            return
        
        if self.current_directory not in self.selected_folders:
            py_count = self.count_python_files_recursive(self.current_directory)
            
            if py_count > 0:
                self.selected_folders.append(self.current_directory)
                self.update_selection_display()
                self.update_action_button_state()
                self.status_label.config(text=f"Dossier ajouté : {os.path.basename(self.current_directory)} ({py_count} fichiers Python)", foreground="green")
            else:
                messagebox.showwarning("Attention", "Ce dossier ne contient aucun fichier Python.")
        else:
            messagebox.showinfo("Information", "Ce dossier est déjà dans la sélection.")
    
    def add_folder_dialog(self):
        """Ouvre un dialog pour ajouter un dossier."""
        folder_path = filedialog.askdirectory(
            title="Sélectionner un dossier à ajouter",
            initialdir=self.current_directory
        )
        
        if folder_path and folder_path not in self.selected_folders:
            py_count = self.count_python_files_recursive(folder_path)
            
            if py_count > 0:
                self.selected_folders.append(folder_path)
                self.update_selection_display()
                self.update_action_button_state()
                self.status_label.config(text=f"Dossier ajouté : {os.path.basename(folder_path)} ({py_count} fichiers Python)", foreground="green")
            else:
                messagebox.showwarning("Attention", "Ce dossier ne contient aucun fichier Python.")
        elif folder_path in self.selected_folders:
            messagebox.showinfo("Information", "Ce dossier est déjà dans la sélection.")
    
    def remove_selected_folder(self):
        """Supprime le dossier sélectionné de la liste."""
        selection = self.folders_listbox.curselection()
        if selection:
            index = selection[0]
            removed_folder = self.selected_folders.pop(index)
            self.update_selection_display()
            self.update_action_button_state()
            self.status_label.config(text=f"Dossier retiré : {os.path.basename(removed_folder)}", foreground="orange")
    
    def clear_all_folders(self):
        """Vide la liste des dossiers sélectionnés."""
        if self.selected_folders:
            if messagebox.askyesno("Confirmation", "Vider toute la sélection de dossiers ?"):
                self.selected_folders = []
                self.update_selection_display()
                self.update_action_button_state()
                self.status_label.config(text="Sélection de dossiers vidée", foreground="orange")
    
    def update_selection_display(self):
        """Met à jour l'affichage des sélections."""
        if self.selection_mode == "file":
            if self.selected_files:
                file_path = self.selected_files[0]
                self.selected_file_label.config(
                    text=f"📄 {os.path.basename(file_path)}\n📁 {os.path.dirname(file_path)}",
                    foreground="black"
                )
            else:
                self.selected_file_label.config(text="Aucun fichier sélectionné", foreground="gray")
        
        else:  # folders
            # Mettre à jour la listbox
            self.folders_listbox.delete(0, tk.END)
            total_files = 0
            
            for folder in self.selected_folders:
                py_count = self.count_python_files_recursive(folder)
                total_files += py_count
                display_text = f"📁 {os.path.basename(folder)} ({py_count} fichiers Python)"
                self.folders_listbox.insert(tk.END, display_text)
            
            # Mettre à jour les statistiques
            if self.selected_folders:
                self.folders_stats_label.config(
                    text=f"{len(self.selected_folders)} dossiers sélectionnés • {total_files} fichiers Python total",
                    foreground="blue"
                )
            else:
                self.folders_stats_label.config(
                    text="Aucun dossier sélectionné",
                    foreground="gray"
                )
    
    def update_action_button_state(self):
        """Met à jour l'état du bouton de sélection."""
        if self.selection_mode == "file":
            self.select_button.config(state=tk.NORMAL if self.selected_files else tk.DISABLED)
        else:
            self.select_button.config(state=tk.NORMAL if self.selected_folders else tk.DISABLED)
    
    def go_parent_directory(self):
        """Remonte au répertoire parent."""
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:
            self.current_directory = parent_dir
            self.populate_tree()
    
    def change_directory(self):
        """Ouvre un dialog pour changer de répertoire."""
        new_directory = filedialog.askdirectory(
            title="Choisir un répertoire",
            initialdir=self.current_directory
        )
        
        if new_directory:
            self.current_directory = new_directory
            self.populate_tree()
    
    def refresh_tree(self):
        """Actualise l'arborescence."""
        self.populate_tree()
    
    def confirm_selection(self):
        """Confirme la sélection et ferme la fenêtre."""
        if self.selection_mode == "file":
            if self.selected_files:
                self.master.quit()
            else:
                messagebox.showwarning("Attention", "Veuillez sélectionner un fichier Python (.py)")
        else:
            if self.selected_folders:
                self.master.quit()
            else:
                messagebox.showwarning("Attention", "Veuillez sélectionner au moins un dossier")
    
    def cancel_selection(self):
        """Annule la sélection et ferme la fenêtre."""
        self.selected_files = []
        self.selected_folders = []
        self.master.quit()
    
    def on_closing(self):
        """Gestionnaire de fermeture de fenêtre."""
        self.cancel_selection()
    
    def show_help(self):
        """Affiche l'aide."""
        help_text = """
Sélecteur de Fichiers/Dossiers Python - Aide

MODES DE SÉLECTION :
📄 Fichier unique : Pour traiter un seul fichier Python
📁 Dossiers multiples : Pour traiter plusieurs dossiers en lot

NAVIGATION :
• Double-cliquez sur un dossier pour y entrer
• "↑ Dossier parent" pour remonter
• "📁 Changer dossier" pour aller ailleurs directement

MODE FICHIER UNIQUE :
• Cliquez sur un fichier Python (.py) pour le sélectionner
• L'aperçu s'affiche automatiquement
• Double-cliquez pour sélectionner directement

MODE DOSSIERS MULTIPLES :
• "➕ Ajouter ce dossier" pour ajouter le dossier actuel
• "➕ Ajouter dossier" pour choisir un dossier ailleurs
• Utilisez l'onglet "Sélection" pour gérer vos dossiers
• Seuls les dossiers contenant des fichiers Python sont acceptés

RACCOURCIS :
• Échap : Annuler
• Entrée : Sélectionner (si des éléments sont choisis)
        """
        
        messagebox.showinfo("Aide - Sélecteur de Fichiers/Dossiers", help_text.strip())


def launch_file_selector():
    """Lance l'interface de sélection et retourne les éléments choisis."""
    
    # Vérification de l'environnement
    if not _check_gui_environment():
        return None, None
    
    try:
        # Créer la fenêtre principale
        root = tk.Tk()
        
        # Créer l'application
        app = FileSelectorApp(root)
        
        # Centrer la fenêtre
        _center_window(root)
        
        # Lancer la boucle principale
        root.mainloop()
        
        # Récupérer les éléments sélectionnés
        if app.selection_mode == "file":
            selected_items = app.selected_files
            selection_type = "file"
        else:
            selected_items = app.selected_folders
            selection_type = "folders"
        
        # Nettoyer
        try:
            root.destroy()
        except:
            pass
        
        return selected_items, selection_type
        
    except Exception as e:
        print(f"Erreur lors du lancement de l'interface GUI : {e}")
        return None, None


def _check_gui_environment():
    """Vérifie si l'environnement supporte l'interface graphique."""
    try:
        # Test de création d'une fenêtre Tkinter
        test_root = tk.Tk()
        test_root.withdraw()  # Cacher la fenêtre
        test_root.destroy()
        return True
    except Exception as e:
        print(f"Interface graphique non disponible : {e}")
        return False


def _center_window(window):
    """Centre une fenêtre sur l'écran."""
    try:
        window.update_idletasks()
        
        # Obtenir les dimensions
        width = window.winfo_width()
        height = window.winfo_height()
        
        # Calculer la position centrale
        pos_x = (window.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (window.winfo_screenheight() // 2) - (height // 2)
        
        # Appliquer la position
        window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        
    except Exception:
        # Si le centrage échoue, laisser la position par défaut
        pass


# ===============================================
# COLLECTEUR DE FICHIERS POUR LE BACKEND
# ===============================================

def collect_python_files_from_selection(selected_items, selection_type):
    """Collecte tous les fichiers Python à partir de la sélection GUI."""
    
    python_files = []
    
    if selection_type == "file":
        # Mode fichier unique
        if selected_items:
            file_path = selected_items[0]
            if os.path.exists(file_path) and file_path.endswith('.py'):
                python_files.append(file_path)
    
    elif selection_type == "folders":
        # Mode dossiers multiples
        for folder_path in selected_items:
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                print(f"! Dossier ignoré (non trouvé) : {folder_path}")
                continue
            
            # Parcours récursif pour collecter les fichiers .py
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        python_files.append(file_path)
                
                # Éviter les dossiers système et cachés
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
    
    return python_files


# ===============================================
# FONCTION D'INTÉGRATION POUR LE BACKEND
# ===============================================

def launch_file_selector_integrated():
    """Lance le sélecteur GUI et retourne la liste des fichiers Python à traiter."""
    
    # Lancer l'interface
    selected_items, selection_type = launch_file_selector()
    
    if not selected_items:
        print("Aucune sélection effectuée")
        return []
    
    # Collecter les fichiers Python
    python_files = collect_python_files_from_selection(selected_items, selection_type)
    
    if not python_files:
        print("Aucun fichier Python trouvé dans la sélection")
        return []
    
    # Afficher un résumé
    print(f"*** SÉLECTION CONFIRMÉE ***")
    if selection_type == "file":
        print(f"Mode : Fichier unique")
        print(f"Fichier : {python_files[0]}")
    else:
        print(f"Mode : Dossiers multiples")
        print(f"Dossiers sélectionnés : {len(selected_items)}")
        print(f"Fichiers Python collectés : {len(python_files)}")
        
        # Afficher un échantillon
        if len(python_files) <= 5:
            for i, file_path in enumerate(python_files, 1):
                print(f"  {i}. {os.path.relpath(file_path)}")
        else:
            for i, file_path in enumerate(python_files[:3], 1):
                print(f"  {i}. {os.path.relpath(file_path)}")
            print(f"  ... et {len(python_files) - 3} autres fichiers")
    
    return python_files


# ===============================================
# FONCTION DE TEST COMPLÈTE
# ===============================================

def test_selector():
    """Fonction de test pour le sélecteur avancé."""
    print("*** Test du Sélecteur de Fichiers/Dossiers GUI ***")
    print("=" * 50)
    
    python_files = launch_file_selector_integrated()
    
    if python_files:
        print(f"\n✅ Résultat final : {len(python_files)} fichier(s) Python prêt(s) pour traitement")
        
        # Statistiques
        total_size = 0
        for file_path in python_files:
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass
        
        print(f"   Taille totale : {format_size_simple(total_size)}")
        print(f"   Premier fichier : {python_files[0]}")
        if len(python_files) > 1:
            print(f"   Dernier fichier : {python_files[-1]}")
        
    else:
        print("❌ Aucun fichier sélectionné ou trouvé")


def format_size_simple(size_bytes):
    """Version simple du formateur de taille."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


if __name__ == '__main__':
    test_selector()