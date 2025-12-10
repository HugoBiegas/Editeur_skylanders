#!/usr/bin/env python3
"""
Skylanders .SKY File Editor v3.0
================================
Éditeur pour fichiers .sky avec détection automatique du jeu d'origine.

FONCTIONNALITÉS v3.0:
- Détection automatique du jeu (SSA, Giants, Swap Force, Trap Team, SuperChargers, Imaginators)
- Niveau maximum adapté selon le jeu détecté
- Interface simplifiée (statistiques uniquement)
- Base de données complète des Skylanders (300+ personnages)

Niveaux max par jeu:
- Spyro's Adventure: 10
- Giants: 15
- Swap Force, Trap Team, SuperChargers, Imaginators: 20

Compatible avec émulateurs RPCS3 et Dolphin.

Auteur: Éditeur Skylanders
Version: 3.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional

# Import de la bibliothèque core
from skylander_core import (
    Skylander, SkylandersGame, 
    MAX_MONEY, MAX_HERO_POINTS,
    XP_TABLE_LEVEL_10, XP_TABLE_LEVEL_15, XP_TABLE_LEVEL_20
)


class SkylanderEditorApp:
    """Application GUI pour l'édition de Skylanders."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Skylanders .SKY Editor v3.0")
        self.root.geometry("580x580")
        self.root.resizable(True, True)
        
        self.skylander: Optional[Skylander] = None
        self.current_file: Optional[str] = None
        
        self._setup_menu()
        self._setup_ui()
    
    def _setup_menu(self) -> None:
        """Configure le menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir .sky...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder sous...", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit, accelerator="Alt+F4")
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self._show_about)
        
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
    
    def _setup_ui(self) -> None:
        """Configure l'interface utilisateur."""
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Section Fichier
        file_frame = ttk.LabelFrame(main, text="Fichier", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_inner = ttk.Frame(file_frame)
        file_inner.pack(fill=tk.X)
        
        self.file_label = ttk.Label(file_inner, text="Aucun fichier chargé", foreground="gray")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(file_inner, text="Ouvrir...", command=self.open_file).pack(side=tk.RIGHT)
        
        # Section Info Skylander
        info_frame = ttk.LabelFrame(main, text="Informations Skylander", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.char_label = ttk.Label(info_frame, text="Personnage: -", font=('TkDefaultFont', 11, 'bold'))
        self.char_label.pack(anchor=tk.W)
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(info_grid, text="Jeu d'origine:").grid(row=0, column=0, sticky=tk.W)
        self.game_label = ttk.Label(info_grid, text="-", foreground="blue")
        self.game_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_grid, text="Niveau max:").grid(row=0, column=2, sticky=tk.W)
        self.maxlevel_label = ttk.Label(info_grid, text="-", foreground="green")
        self.maxlevel_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(info_grid, text="Variant ID:").grid(row=1, column=0, sticky=tk.W)
        self.variant_label = ttk.Label(info_grid, text="-")
        self.variant_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Section Stats (modifiables)
        stats_frame = ttk.LabelFrame(main, text="Statistiques (Modifiables)", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # XP
        row = 0
        ttk.Label(stats_frame, text="Expérience (XP):").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.xp_var = tk.StringVar()
        self.xp_entry = ttk.Entry(stats_frame, textvariable=self.xp_var, width=15)
        self.xp_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.xp_max_label = ttk.Label(stats_frame, text="(max: -)")
        self.xp_max_label.grid(row=row, column=2, sticky=tk.W)
        
        # Niveau
        row += 1
        ttk.Label(stats_frame, text="Niveau:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.level_var = tk.StringVar()
        self.level_combo = ttk.Combobox(stats_frame, textvariable=self.level_var, width=6, state='readonly')
        self.level_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        self.level_combo.bind('<<ComboboxSelected>>', self._on_level_change)
        self.level_info_label = ttk.Label(stats_frame, text="(sélectionnez pour ajuster l'XP)")
        self.level_info_label.grid(row=row, column=2, sticky=tk.W)
        
        # Argent
        row += 1
        ttk.Label(stats_frame, text="Argent:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.money_var = tk.StringVar()
        self.money_entry = ttk.Entry(stats_frame, textvariable=self.money_var, width=15)
        self.money_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, text=f"(max: {MAX_MONEY:,})").grid(row=row, column=2, sticky=tk.W)
        
        # Heroic Challenges (anciennement "Points Héroïques")
        row += 1
        ttk.Label(stats_frame, text="Heroics:").grid(row=row, column=0, sticky=tk.W, pady=3)
        self.hero_var = tk.StringVar()
        self.hero_entry = ttk.Entry(stats_frame, textvariable=self.hero_var, width=15)
        self.hero_entry.grid(row=row, column=1, sticky=tk.W, padx=5)
        ttk.Label(stats_frame, text=f"(max: {MAX_HERO_POINTS}, challenges complétés)").grid(row=row, column=2, sticky=tk.W)
        
        # Boutons d'action
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.apply_btn = ttk.Button(btn_frame, text="✓ Appliquer les modifications", command=self.apply_changes, state='disabled')
        self.apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.max_btn = ttk.Button(btn_frame, text="⬆ Max Stats", command=self.max_stats, state='disabled')
        self.max_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_btn = ttk.Button(btn_frame, text="↺ Reset Stats", command=self.reset_stats, state='disabled')
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_btn = ttk.Button(btn_frame, text="💾 Sauvegarder", command=self.save_file, state='disabled')
        self.save_btn.pack(side=tk.RIGHT)
        
        # Vue Hex
        hex_frame = ttk.LabelFrame(main, text="Vue Hexadécimale (Header déchiffré)", padding="5")
        hex_frame.pack(fill=tk.BOTH, expand=True)
        
        self.hex_text = tk.Text(hex_frame, height=8, font=('Consolas', 9), state='disabled', bg='#f5f5f5')
        scroll = ttk.Scrollbar(hex_frame, command=self.hex_text.yview)
        self.hex_text.configure(yscrollcommand=scroll.set)
        self.hex_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Barre de statut
        status_frame = ttk.Frame(main)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Prêt - Ouvrez un fichier .sky pour commencer")
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)
    
    def _on_level_change(self, event=None) -> None:
        """Callback quand le niveau change."""
        if not self.skylander:
            return
        try:
            level = int(self.level_var.get())
            xp_table = self.skylander.get_xp_table()
            if 1 <= level < len(xp_table):
                self.xp_var.set(str(xp_table[level]))
        except ValueError:
            pass
    
    def _refresh_display(self) -> None:
        """Rafraîchit l'affichage avec les données du Skylander."""
        if not self.skylander:
            return
        
        name, game = self.skylander.get_character_info()
        max_level = self.skylander.get_max_level()
        max_xp = self.skylander.get_max_xp()
        
        # Info
        self.char_label.config(text=f"Personnage: {name}")
        self.game_label.config(text=game.display_name)
        self.variant_label.config(text=f"0x{self.skylander.get_variant_id():04X}")
        self.maxlevel_label.config(text=str(max_level))
        
        # Mettre à jour les labels de max
        self.xp_max_label.config(text=f"(max: {max_xp:,})")
        
        # Mettre à jour la combobox des niveaux
        self.level_combo['values'] = [str(i) for i in range(1, max_level + 1)]
        
        # Stats
        self.xp_var.set(str(self.skylander.get_xp()))
        self.level_var.set(str(self.skylander.get_level()))
        self.money_var.set(str(self.skylander.get_money()))
        self.hero_var.set(str(self.skylander.get_hero_points()))
        
        # Activer les boutons
        self.apply_btn.config(state='normal')
        self.max_btn.config(state='normal')
        self.reset_btn.config(state='normal')
        self.save_btn.config(state='normal')
        
        # Hex view (premier 256 octets)
        self.hex_text.configure(state='normal')
        self.hex_text.delete(1.0, tk.END)
        for i in range(0, 256, 16):
            hex_part = ' '.join(f'{b:02X}' for b in self.skylander.data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in self.skylander.data[i:i+16])
            self.hex_text.insert(tk.END, f'{i:04X}  {hex_part:<48}  {ascii_part}\n')
        self.hex_text.configure(state='disabled')
    
    def open_file(self) -> None:
        """Ouvre un fichier .sky."""
        filename = filedialog.askopenfilename(
            title="Ouvrir fichier Skylander",
            filetypes=[("SKY Files", "*.sky"), ("Tous les fichiers", "*.*")]
        )
        if not filename:
            return
        
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            self.skylander = Skylander(data)
            self.skylander.decrypt()
            self.current_file = filename
            
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            self._refresh_display()
            
            name, game = self.skylander.get_character_info()
            self.status_var.set(f"✓ Chargé: {name} ({game.display_name}) - Niveau max: {game.max_level}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")
    
    def save_file(self) -> None:
        """Sauvegarde le fichier .sky."""
        if not self.skylander:
            messagebox.showwarning("Attention", "Aucun Skylander chargé!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder",
            filetypes=[("SKY Files", "*.sky")],
            defaultextension=".sky",
            initialfile=os.path.basename(self.current_file) if self.current_file else ""
        )
        if not filename:
            return
        
        try:
            self.skylander.update_checksums()
            encrypted = self.skylander.encrypt()
            
            with open(filename, 'wb') as f:
                f.write(encrypted)
            
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))
            self.status_var.set(f"✓ Sauvegardé: {os.path.basename(filename)}")
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!\n\nLes checksums ont été recalculés automatiquement.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")
    
    def apply_changes(self) -> None:
        """Applique les modifications."""
        if not self.skylander:
            return
        
        try:
            xp = int(self.xp_var.get())
            money = int(self.money_var.get())
            hero = int(self.hero_var.get())
            
            self.skylander.set_xp(xp)
            self.skylander.set_money(money)
            self.skylander.set_hero_points(hero)
            
            self._refresh_display()
            self.status_var.set("✓ Modifications appliquées! N'oubliez pas de sauvegarder.")
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Valeur invalide:\n{e}\n\nVeuillez entrer des nombres entiers.")
    
    def max_stats(self) -> None:
        """Met toutes les stats au maximum."""
        if not self.skylander:
            return
        
        self.skylander.max_out()
        self._refresh_display()
        
        max_level = self.skylander.get_max_level()
        self.status_var.set(f"✓ Stats au maximum! Niveau {max_level}, Argent {MAX_MONEY:,}, Heroics {MAX_HERO_POINTS}")
    
    def reset_stats(self) -> None:
        """Remet toutes les stats à zéro."""
        if not self.skylander:
            return
        
        if messagebox.askyesno("Confirmer", "Remettre toutes les stats à zéro?\n\n(XP, Argent, Heroic Challenges)"):
            self.skylander.reset_stats()
            self._refresh_display()
            self.status_var.set("↺ Stats réinitialisées à zéro!")
    
    def _show_about(self) -> None:
        """Affiche la fenêtre À propos."""
        about_text = """Skylanders .SKY File Editor v3.0

Éditeur de fichiers .sky pour les émulateurs Skylanders (RPCS3, Dolphin).

Fonctionnalités:
• Détection automatique du jeu d'origine
• Niveau maximum adapté par jeu:
  - Spyro's Adventure: Level 10
  - Giants: Level 15
  - Swap Force et suivants: Level 20
• Édition des statistiques (XP, Argent, Heroic Challenges)
• Recalcul automatique des checksums

Compatible avec 300+ Skylanders de tous les jeux.

⚠️ Faites toujours une sauvegarde avant modification!
"""
        messagebox.showinfo("À propos", about_text)


def main():
    """Point d'entrée principal."""
    root = tk.Tk()
    
    # Icône (si disponible)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = SkylanderEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
