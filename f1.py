"""
F1 Desktop Pro - Ultimate Edition
Professional F1 Data Analysis mit Standings & Championships

Neue Features:
- Race Results & Podium
- Driver Championship Standings
- Constructor Championship Standings
- Team Colors & Styling
- Points Progression
- Head-to-Head Stats
- Visual Podium Display
"""

import sys
import subprocess
import os

from f1desktoppro.config import get_app_data_dir, load_config, save_config
from f1desktoppro.data_service import F1DataService
from f1desktoppro.licensing import is_valid_key, trial_status
from f1desktoppro.logging_setup import setup_logging

def check_and_install_packages():
    required_packages = {
        'fastf1': 'fastf1',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'customtkinter': 'customtkinter',
        'PIL': 'Pillow'
    }
    
    optional_packages = {
        'scipy': 'scipy',
        'openpyxl': 'openpyxl',
        'seaborn': 'seaborn',
        'requests': 'requests'
    }
    
    missing_required = []
    missing_optional = []
    
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_required.append(package_name)
    
    for module_name, package_name in optional_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_optional.append(package_name)
    
    if not missing_required and not missing_optional:
        return True
    
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        message = "Fehlende Bibliotheken:\n\n"
        if missing_required:
            message += "ERFORDERLICH:\n" + "\n".join(f"  • {pkg}" for pkg in missing_required) + "\n\n"
        if missing_optional:
            message += "OPTIONAL:\n" + "\n".join(f"  • {pkg}" for pkg in missing_optional) + "\n\n"
        message += "Jetzt installieren?"
        
        result = messagebox.askyesno("Installation", message, icon='question')
        root.destroy()
        
        if not result:
            return False
        
    except ImportError:
        print("\n" + "="*60)
        print("WARNUNG: Fehlende Bibliotheken!")
        print("="*60)
        if missing_required:
            print("\nERFORDERLICH:")
            for pkg in missing_required:
                print(f"  • {pkg}")
        if missing_optional:
            print("\nOPTIONAL:")
            for pkg in missing_optional:
                print(f"  • {pkg}")
        print("\n" + "="*60)
        response = input("\nInstallieren? (j/n): ")
        if response.lower() not in ['j', 'ja', 'y', 'yes']:
            return False
    
    packages_to_install = missing_required + missing_optional
    
    if packages_to_install:
        print(f"\n📦 Installiere {len(packages_to_install)} Paket(e)...\n")
        
        try:
            for package in packages_to_install:
                print(f"⏳ {package}...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(f"✅ {package}")
            
            print("\n" + "="*60)
            print("✅ Installation abgeschlossen!")
            print("="*60)
            print("\n🔄 Neustart...\n")
            
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Fehler: {str(e)}")
            return False
    
    return True


def check_dependencies():
    required_packages = {
        "fastf1": "fastf1",
        "pandas": "pandas",
        "numpy": "numpy",
        "matplotlib": "matplotlib",
        "customtkinter": "customtkinter",
        "PIL": "Pillow",
    }

    missing_required = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_required.append(package_name)

    if not missing_required:
        return True

    message = (
        "Fehlende Bibliotheken:\n\n"
        + "\n".join(f"- {pkg}" for pkg in missing_required)
        + "\n\nBitte installiere die Abhaengigkeiten ueber:\n"
        + "pip install -r requirements.txt"
    )

    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fehlende Abhaengigkeiten", message)
        root.destroy()
    except Exception:
        print(message)
    return False


def ensure_license(config):
    if is_valid_key(config.license_key):
        return True

    trial_ok, remaining = trial_status(config.trial_start)
    if trial_ok:
        if not config.trial_start:
            config.trial_start = datetime.utcnow().isoformat()
            save_config(config)
        return True

    try:
        import tkinter as tk
        from tkinter import messagebox, simpledialog

        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Lizenz erforderlich",
            "Die Testphase ist abgelaufen. Bitte Lizenzschluessel eingeben.",
        )
        key = simpledialog.askstring("Lizenz", "Lizenzschluessel:")
        root.destroy()
    except Exception:
        key = None

    if key and is_valid_key(key):
        config.license_key = key
        save_config(config)
        return True

    return False


import fastf1
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
from tkinter import ttk as tk_ttk

import threading
from datetime import datetime
from typing import Optional, List, Dict

try:
    import seaborn as sns
    sns.set_style("darkgrid")
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False

# === TEAM COLORS ===
TEAM_COLORS = {
    'Red Bull Racing': '#3671C6',
    'Ferrari': '#E8002D',
    'Mercedes': '#27F4D2',
    'McLaren': '#FF8000',
    'Aston Martin': '#229971',
    'Alpine': '#FF87BC',
    'Williams': '#64C4FF',
    'AlphaTauri': '#5E8FAA',
    'Alfa Romeo': '#C92D4B',
    'Haas F1 Team': '#B6BABD',
    'RB': '#6692FF',
    'Kick Sauber': '#52E252',
    'Racing Bulls': '#6692FF'
}

# === FARB-PALETTE ===
class ColorPalette:
    F1_RED = "#e10600"
    F1_RED_HOVER = "#ff1a1a"
    
    BG_DARK = "#0a0a0a"
    BG_CARD = "#1a1a1a"
    BG_ELEVATED = "#252525"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    BORDER = "#3d3d3d"
    
    ACCENT_BLUE = "#00aaff"
    ACCENT_GREEN = "#00d4aa"
    ACCENT_ORANGE = "#ffaa00"
    ACCENT_PURPLE = "#aa00ff"
    
    SUCCESS = "#00c853"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"
    
    GOLD = "#FFD700"
    SILVER = "#C0C0C0"
    BRONZE = "#CD7F32"


class AnimatedLabel(ctk.CTkLabel):
    """Label mit Counter-Animation"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_value = 0
        self.current_value = 0
        
    def animate_to(self, value: float, duration: int = 500, format_str: str = "{}"):
        """Animiert zu einem Zielwert"""
        self.target_value = value
        steps = 20
        step_duration = duration // steps
        step_value = (value - self.current_value) / steps
        
        def update_step(step=0):
            if step < steps:
                self.current_value += step_value
                self.configure(text=format_str.format(int(self.current_value)))
                self.after(step_duration, lambda: update_step(step + 1))
            else:
                self.current_value = value
                self.configure(text=format_str.format(int(value)))
        
        update_step()


class StatCard(ctk.CTkFrame):
    """Moderne Statistik-Karte"""
    def __init__(self, parent, title: str, icon: str = "📊", **kwargs):
        super().__init__(parent, fg_color=ColorPalette.BG_CARD, 
                        corner_radius=12, **kwargs)
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(header, text=title, 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=ColorPalette.TEXT_SECONDARY).pack(side="left")
        
        self.value_label = AnimatedLabel(self, text="—", 
                                        font=ctk.CTkFont(size=32, weight="bold"),
                                        text_color=ColorPalette.TEXT_PRIMARY)
        self.value_label.pack(pady=(5, 10))
        
        self.subtext_label = ctk.CTkLabel(self, text="", 
                                         font=ctk.CTkFont(size=10),
                                         text_color=ColorPalette.TEXT_SECONDARY)
        self.subtext_label.pack(pady=(0, 15))
    
    def set_value(self, value: str, subtext: str = "", animate: bool = False):
        """Setzt den Wert der Karte"""
        if animate and isinstance(value, (int, float)):
            self.value_label.animate_to(value)
        else:
            self.value_label.configure(text=str(value))
        self.subtext_label.configure(text=subtext)


class LoadingOverlay(ctk.CTkFrame):
    """Loading Overlay mit Animation"""
    def __init__(self, parent):
        super().__init__(parent, fg_color=("gray90", "gray10"))
        
        container = ctk.CTkFrame(self, fg_color=ColorPalette.BG_CARD,
                                corner_radius=20)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        self.progress = ctk.CTkProgressBar(container, width=300, height=8,
                                          fg_color=ColorPalette.BORDER,
                                          progress_color=ColorPalette.F1_RED)
        self.progress.pack(padx=40, pady=(40, 10))
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(container, text="Lädt...",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(pady=(10, 40))
        
        self.place_forget()
    
    def show(self, message: str = "Lädt..."):
        """Zeigt das Overlay"""
        self.status_label.configure(text=message)
        self.progress.set(0)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.animate_progress()
    
    def hide(self):
        """Versteckt das Overlay"""
        self.place_forget()
    
    def animate_progress(self):
        """Animiert die Progress Bar"""
        current = self.progress.get()
        if current < 0.9:
            self.progress.set(current + 0.1)
            self.after(100, self.animate_progress)
    
    def set_progress(self, value: float):
        """Setzt den Fortschritt manuell"""
        self.progress.set(min(value, 1.0))


class PodiumDisplay(ctk.CTkFrame):
    """Podium-Anzeige für Top 3"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.podium_frames = {}
        
        # Container für Podium
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True)
        
        # 2. Platz (Links)
        self.podium_frames[2] = self.create_podium_place(container, 2, ColorPalette.SILVER, 150)
        self.podium_frames[2].pack(side="left", padx=10, pady=30)
        
        # 1. Platz (Mitte, höher)
        self.podium_frames[1] = self.create_podium_place(container, 1, ColorPalette.GOLD, 180)
        self.podium_frames[1].pack(side="left", padx=10)
        
        # 3. Platz (Rechts)
        self.podium_frames[3] = self.create_podium_place(container, 3, ColorPalette.BRONZE, 130)
        self.podium_frames[3].pack(side="left", padx=10, pady=50)
    
    def create_podium_place(self, parent, position: int, color: str, height: int):
        """Erstellt einen Podiumsplatz"""
        frame = ctk.CTkFrame(parent, fg_color=ColorPalette.BG_CARD,
                           corner_radius=15, width=200, height=height + 100)
        frame.pack_propagate(False)
        
        # Position Badge
        badge = ctk.CTkFrame(frame, fg_color=color, corner_radius=25,
                           width=50, height=50)
        badge.pack(pady=(15, 10))
        badge.pack_propagate(False)
        
        badge_text_color = "#000000"  # Schwarzer Text für alle Badges
        ctk.CTkLabel(badge, text=str(position),
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=badge_text_color).pack(expand=True)
        
        # Driver Name
        frame.driver_label = ctk.CTkLabel(frame, text="—",
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         text_color=ColorPalette.TEXT_PRIMARY)
        frame.driver_label.pack(pady=5)
        
        # Team
        frame.team_label = ctk.CTkLabel(frame, text="",
                                       font=ctk.CTkFont(size=11),
                                       text_color=ColorPalette.TEXT_SECONDARY)
        frame.team_label.pack()
        
        # Time/Gap
        frame.time_label = ctk.CTkLabel(frame, text="",
                                       font=ctk.CTkFont(size=13),
                                       text_color=ColorPalette.TEXT_PRIMARY)
        frame.time_label.pack(pady=5)
        
        # Points
        frame.points_label = ctk.CTkLabel(frame, text="",
                                         font=ctk.CTkFont(size=12, weight="bold"),
                                         text_color=color)
        frame.points_label.pack(pady=5)
        
        # Podium Base
        base = ctk.CTkFrame(frame, fg_color=color, corner_radius=0,
                          height=height)
        base.pack(side="bottom", fill="x")
        base.pack_propagate(False)
        
        base_text_color = "#000000"  # Schwarzer Text für alle Sockel
        ctk.CTkLabel(base, text=f"P{position}",
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color=base_text_color).pack(expand=True)
        
        return frame
    
    def set_position(self, position: int, driver: str, team: str, time: str, points: int):
        """Setzt Daten für eine Position"""
        if position in self.podium_frames:
            frame = self.podium_frames[position]
            
            # Truncate long names
            display_driver = driver[:8] if len(driver) > 8 else driver
            display_team = team[:15] + "..." if len(team) > 15 else team
            
            frame.driver_label.configure(text=display_driver)
            frame.team_label.configure(text=display_team)
            frame.time_label.configure(text=time)
            frame.points_label.configure(text=f"{points} Punkte")

    def clear(self):
        """Setzt das Podium zurck"""
        for frame in self.podium_frames.values():
            frame.driver_label.configure(text="-")
            frame.team_label.configure(text="")
            frame.time_label.configure(text="")
            frame.points_label.configure(text="")


class F1DesktopPro:
    def __init__(self, root, config=None, logger=None):
        self.root = root
        self.config = config
        self.logger = logger
        self.data_service = F1DataService()
        self.root.title("🏎️ F1 Desktop Pro - Ultimate Edition")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        
        # State
        self.session = None
        self.events = None
        self.current_lap = None
        self.sort_column = None
        self.sort_reverse = False
        self.filter_text = ""
        self.theme = "dark"
        
        # Colors
        self.colors = ColorPalette()
        
        # UI
        self.build_ui()

        # Loading Overlay
        self.loading = LoadingOverlay(self.root)

        self.load_years()

    def build_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self.root, width=280, 
                                   fg_color=ColorPalette.BG_CARD,
                                   corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        self.build_sidebar()
        
        # === MAIN CONTENT ===
        self.main_container = ctk.CTkFrame(self.root, 
                                          fg_color=ColorPalette.BG_DARK)
        self.main_container.pack(side="right", fill="both", expand=True)
        
        self.build_main_content()

    def build_sidebar(self):
        """Erstellt die Sidebar"""
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="🏎️", font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(header, text="F1 Desktop Pro",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(5, 0))
        ctk.CTkLabel(header, text="Ultimate Edition",
                    font=ctk.CTkFont(size=10),
                    text_color=ColorPalette.TEXT_SECONDARY).pack()
        
        ctk.CTkFrame(self.sidebar, height=2, 
                    fg_color=ColorPalette.BORDER).pack(fill="x", padx=20, pady=10)
        
        controls = ctk.CTkScrollableFrame(self.sidebar, 
                                         fg_color="transparent")
        controls.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Jahr
        self.create_control_section(controls, "Jahr", "📅")
        self.year_var = ctk.StringVar()
        self.year_cb = ctk.CTkComboBox(controls, variable=self.year_var,
                                       width=250, state="readonly",
                                       command=self.on_year_selected,
                                       fg_color=ColorPalette.BG_ELEVATED,
                                       button_color=ColorPalette.F1_RED,
                                       button_hover_color=ColorPalette.F1_RED_HOVER)
        self.year_cb.pack(pady=(5, 15))
        
        # Grand Prix
        self.create_control_section(controls, "Grand Prix", "🏁")
        self.gp_var = ctk.StringVar()
        self.gp_cb = ctk.CTkComboBox(controls, variable=self.gp_var,
                                     width=250, state="readonly",
                                     fg_color=ColorPalette.BG_ELEVATED,
                                     button_color=ColorPalette.F1_RED,
                                     button_hover_color=ColorPalette.F1_RED_HOVER)
        self.gp_cb.pack(pady=(5, 15))
        
        # Session
        self.create_control_section(controls, "Session", "⏱️")
        self.ses_var = ctk.StringVar()
        self.ses_cb = ctk.CTkComboBox(controls, variable=self.ses_var,
                                     values=["FP1", "FP2", "FP3", "Q", "R"],
                                     width=250, state="readonly",
                                     fg_color=ColorPalette.BG_ELEVATED,
                                     button_color=ColorPalette.F1_RED,
                                     button_hover_color=ColorPalette.F1_RED_HOVER)
        self.ses_cb.pack(pady=(5, 15))
        if self.config and self.config.last_session in ["FP1", "FP2", "FP3", "Q", "R"]:
            self.ses_var.set(self.config.last_session)
        
        # Load Button
        self.load_btn = ctk.CTkButton(controls, text="🚀 Session laden",
                                     command=self.load_session,
                                     fg_color=ColorPalette.F1_RED,
                                     hover_color=ColorPalette.F1_RED_HOVER,
                                     height=45, corner_radius=10,
                                     font=ctk.CTkFont(size=14, weight="bold"))
        self.load_btn.pack(pady=20, fill="x")
        
        ctk.CTkFrame(controls, height=2,
                    fg_color=ColorPalette.BORDER).pack(fill="x", pady=15)
        
        # Quick Actions
        ctk.CTkLabel(controls, text="Quick Actions",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=ColorPalette.TEXT_SECONDARY).pack(anchor="w", pady=(0, 10))
        
        actions = [
            ("🏆 Championship", self.show_championship, ColorPalette.GOLD, "#000000"),
            ("💾 Export Daten", self.export_data, ColorPalette.ACCENT_BLUE, ColorPalette.TEXT_PRIMARY),
            ("📊 Export Charts", self.export_plot, ColorPalette.ACCENT_GREEN, ColorPalette.TEXT_PRIMARY),
            ("🔄 Reset View", self.reset_view, ColorPalette.ACCENT_ORANGE, ColorPalette.TEXT_PRIMARY)
        ]
        
        for text, command, color, text_color in actions:
            btn = ctk.CTkButton(controls, text=text, command=command,
                               fg_color=color, hover_color=color,
                               text_color=text_color,
                               height=35, corner_radius=8,
                               font=ctk.CTkFont(size=12, weight="bold"))
            btn.pack(pady=5, fill="x")
        
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(footer, text="FastF1 Data Analysis",
                    font=ctk.CTkFont(size=9),
                    text_color=ColorPalette.TEXT_SECONDARY).pack()

    def create_control_section(self, parent, title: str, icon: str):
        """Erstellt einen Control-Section Header"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(5, 0))
        
        ctk.CTkLabel(frame, text=icon, 
                    font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(frame, text=title,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=ColorPalette.TEXT_SECONDARY).pack(side="left")

    def build_main_content(self):
        """Erstellt den Hauptinhalt"""
        # Header Bar
        header = ctk.CTkFrame(self.main_container, 
                             fg_color=ColorPalette.BG_CARD,
                             height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        self.session_title = ctk.CTkLabel(title_frame, 
                                         text="Keine Session geladen",
                                         font=ctk.CTkFont(size=20, weight="bold"))
        self.session_title.pack(anchor="w")
        
        self.session_subtitle = ctk.CTkLabel(title_frame,
                                            text="Wähle eine Session aus der Sidebar",
                                            font=ctk.CTkFont(size=11),
                                            text_color=ColorPalette.TEXT_SECONDARY)
        self.session_subtitle.pack(anchor="w")
        
        # Search Bar
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        ctk.CTkLabel(search_frame, text="🔍",
                    font=ctk.CTkFont(size=16)).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(search_frame, 
                                        placeholder_text="Fahrer, Team suchen...",
                                        width=250, height=35,
                                        fg_color=ColorPalette.BG_ELEVATED,
                                        border_width=0)
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)
        
        # Content Area
        content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Dashboard
        self.build_dashboard(content)
        
        # Tabs
        self.build_tabs(content)

    def build_dashboard(self, parent):
        """Erstellt das Dashboard mit Stat-Cards"""
        dashboard = ctk.CTkFrame(parent, fg_color="transparent")
        dashboard.pack(fill="x", pady=(0, 15))
        
        stats_grid = ctk.CTkFrame(dashboard, fg_color="transparent")
        stats_grid.pack(fill="x")
        
        for i in range(6):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        self.stat_cards = {}
        
        cards_config = [
            ("best_time", "Beste Zeit", "⏱️"),
            ("fastest_driver", "Schnellster", "👤"),
            ("total_laps", "Runden", "🔄"),
            ("total_drivers", "Fahrer", "👥"),
            ("avg_speed", "Ø Tempo", "🏎️"),
            ("best_sector", "Bester Sektor", "📊")
        ]
        
        for i, (key, title, icon) in enumerate(cards_config):
            card = StatCard(stats_grid, title=title, icon=icon, width=200)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.stat_cards[key] = card

    def build_tabs(self, parent):
        """Erstellt die Tab-Ansicht"""
        self.tab_view = ctk.CTkTabview(parent, 
                                      fg_color=ColorPalette.BG_CARD,
                                      segmented_button_fg_color=ColorPalette.BG_ELEVATED,
                                      segmented_button_selected_color=ColorPalette.F1_RED,
                                      segmented_button_selected_hover_color=ColorPalette.F1_RED_HOVER)
        self.tab_view.pack(fill="both", expand=True)
        
        # Tabs
        self.tab_view.add("📊 Übersicht")
        self.tab_view.add("🏆 Standings")
        self.tab_view.add("📈 Telemetrie")
        self.tab_view.add("⚖️ Vergleich")
        self.tab_view.add("🎯 Analyse")
        
        # Tab Contents
        self.build_overview_tab()
        self.build_standings_tab()
        self.build_telemetry_tab()
        self.build_compare_tab()
        self.build_analysis_tab()

    def build_standings_tab(self):
        """Erstellt den Standings-Tab"""
        tab = self.tab_view.tab("🏆 Standings")
        
        # Sub-tabs
        standings_tabs = ctk.CTkTabview(tab,
                                       fg_color="transparent",
                                       segmented_button_fg_color=ColorPalette.BG_ELEVATED,
                                       segmented_button_selected_color=ColorPalette.ACCENT_BLUE)
        standings_tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        standings_tabs.add("🏁 Race Results")
        standings_tabs.add("👤 Driver Championship")
        standings_tabs.add("🏢 Constructor Championship")
        
        # Race Results Tab
        self.build_race_results_tab(standings_tabs.tab("🏁 Race Results"))
        
        # Driver Championship Tab
        self.build_driver_championship_tab(standings_tabs.tab("👤 Driver Championship"))
        
        # Constructor Championship Tab
        self.build_constructor_championship_tab(standings_tabs.tab("🏢 Constructor Championship"))

    def build_race_results_tab(self, parent):
        """Erstellt Race Results Tab"""
        # Info message if not a race
        self.race_info_label = ctk.CTkLabel(parent, 
                                           text="Lade eine Race-Session (R), um Ergebnisse zu sehen",
                                           font=ctk.CTkFont(size=14),
                                           text_color=ColorPalette.TEXT_SECONDARY)
        self.race_info_label.pack(pady=20)
        
        # Podium Display
        podium_container = ctk.CTkFrame(parent, fg_color=ColorPalette.BG_ELEVATED,
                                       corner_radius=15, height=300)
        podium_container.pack(fill="x", padx=10, pady=(10, 5))
        podium_container.pack_propagate(False)
        
        ctk.CTkLabel(podium_container, text="🏆 PODIUM",
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        self.podium = PodiumDisplay(podium_container)
        self.podium.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Results Table
        table_container = ctk.CTkFrame(parent, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        table_header = ctk.CTkFrame(table_container, fg_color="transparent")
        table_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(table_header, text="📋 Vollständiges Ergebnis",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Table
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar_y = tk.Scrollbar(table_frame, orient="vertical")
        
        style = tk_ttk.Style()
        style.theme_use("clam")
        style.configure("Results.Treeview",
                       background=ColorPalette.BG_CARD,
                       foreground=ColorPalette.TEXT_PRIMARY,
                       fieldbackground=ColorPalette.BG_CARD,
                       borderwidth=0,
                       rowheight=35)
        style.configure("Results.Treeview.Heading",
                       background=ColorPalette.BG_ELEVATED,
                       foreground=ColorPalette.TEXT_PRIMARY,
                       borderwidth=1)
        style.map("Results.Treeview",
                 background=[("selected", ColorPalette.F1_RED)])
        
        columns = ("Pos", "Fahrer", "Team", "Zeit", "Punkte", "Status")
        self.results_table = tk_ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Results.Treeview"
        )
        
        scrollbar_y.config(command=self.results_table.yview)
        
        widths = {"Pos": 60, "Fahrer": 150, "Team": 200, "Zeit": 120, 
                 "Punkte": 100, "Status": 150}
        
        for col in columns:
            self.results_table.heading(col, text=col)
            self.results_table.column(col, width=widths.get(col, 100), anchor="center")
        
        self.results_table.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

    def build_driver_championship_tab(self, parent):
        """Erstellt Driver Championship Tab"""
        # Split view
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Standings Table
        table_container = ctk.CTkFrame(left, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        table_container.pack(fill="both", expand=True)
        
        ctk.CTkLabel(table_container, text="👤 Fahrer-WM",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar_y = tk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("Pos", "Fahrer", "Team", "Punkte", "Siege")
        self.driver_standings_table = tk_ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Results.Treeview"
        )
        
        scrollbar_y.config(command=self.driver_standings_table.yview)
        
        widths = {"Pos": 60, "Fahrer": 150, "Team": 150, "Punkte": 100, "Siege": 80}
        
        for col in columns:
            self.driver_standings_table.heading(col, text=col)
            self.driver_standings_table.column(col, width=widths.get(col, 100), 
                                             anchor="center")
        
        self.driver_standings_table.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        
        # Points Chart
        chart_container = ctk.CTkFrame(right, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        chart_container.pack(fill="both", expand=True)
        
        ctk.CTkLabel(chart_container, text="📈 Punkte-Entwicklung",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.driver_points_fig = Figure(figsize=(6, 5), facecolor=ColorPalette.BG_CARD)
        self.driver_points_ax = self.driver_points_fig.add_subplot(111, 
                                                                   facecolor=ColorPalette.BG_ELEVATED)
        self.driver_points_canvas = FigureCanvasTkAgg(self.driver_points_fig, 
                                                     master=chart_container)
        self.driver_points_canvas.get_tk_widget().pack(fill="both", expand=True, 
                                                      padx=10, pady=10)
        self.style_plot(self.driver_points_ax)

    def build_constructor_championship_tab(self, parent):
        """Erstellt Constructor Championship Tab"""
        # Split view
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Standings Table
        table_container = ctk.CTkFrame(left, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        table_container.pack(fill="both", expand=True)
        
        ctk.CTkLabel(table_container, text="🏢 Konstrukteurs-WM",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar_y = tk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("Pos", "Team", "Punkte", "Siege")
        self.constructor_standings_table = tk_ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Results.Treeview"
        )
        
        scrollbar_y.config(command=self.constructor_standings_table.yview)
        
        widths = {"Pos": 80, "Team": 250, "Punkte": 120, "Siege": 100}
        
        for col in columns:
            self.constructor_standings_table.heading(col, text=col)
            self.constructor_standings_table.column(col, width=widths.get(col, 100), 
                                                  anchor="center")
        
        self.constructor_standings_table.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        
        # Points Chart
        chart_container = ctk.CTkFrame(right, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        chart_container.pack(fill="both", expand=True)
        
        ctk.CTkLabel(chart_container, text="📊 Team-Vergleich",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.constructor_points_fig = Figure(figsize=(6, 5), 
                                            facecolor=ColorPalette.BG_CARD)
        self.constructor_points_ax = self.constructor_points_fig.add_subplot(111,
                                                                             facecolor=ColorPalette.BG_ELEVATED)
        self.constructor_points_canvas = FigureCanvasTkAgg(self.constructor_points_fig,
                                                          master=chart_container)
        self.constructor_points_canvas.get_tk_widget().pack(fill="both", expand=True,
                                                           padx=10, pady=10)
        self.style_plot(self.constructor_points_ax)

    def build_overview_tab(self):
        """Erstellt den Übersichts-Tab"""
        tab = self.tab_view.tab("📊 Übersicht")
        
        table_container = ctk.CTkFrame(tab, fg_color=ColorPalette.BG_ELEVATED,
                                      corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        table_header = ctk.CTkFrame(table_container, fg_color="transparent")
        table_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(table_header, text="🏁 Rundenzeiten",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar_y = tk.Scrollbar(table_frame, orient="vertical")
        scrollbar_x = tk.Scrollbar(table_frame, orient="horizontal")
        
        style = tk_ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                       background=ColorPalette.BG_CARD,
                       foreground=ColorPalette.TEXT_PRIMARY,
                       fieldbackground=ColorPalette.BG_CARD,
                       borderwidth=0,
                       rowheight=30)
        style.configure("Custom.Treeview.Heading",
                       background=ColorPalette.BG_ELEVATED,
                       foreground=ColorPalette.TEXT_PRIMARY,
                       borderwidth=1,
                       relief="flat")
        style.map("Custom.Treeview",
                 background=[("selected", ColorPalette.F1_RED)],
                 foreground=[("selected", ColorPalette.TEXT_PRIMARY)])
        
        columns = ("Pos", "Fahrer", "Team", "Runde", "Zeit", "S1", "S2", "S3", "Tempo", "★")
        self.lap_table = tk_ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            style="Custom.Treeview"
        )
        
        scrollbar_y.config(command=self.lap_table.yview)
        scrollbar_x.config(command=self.lap_table.xview)
        
        widths = {"Pos": 60, "Fahrer": 120, "Team": 150, "Runde": 80,
                 "Zeit": 110, "S1": 90, "S2": 90, "S3": 90, "Tempo": 100, "★": 50}
        
        for col in columns:
            self.lap_table.heading(col, text=col, 
                                  command=lambda c=col: self.sort_table(c))
            self.lap_table.column(col, width=widths.get(col, 100), anchor="center")
        
        self.lap_table.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.lap_table.bind("<<TreeviewSelect>>", self.on_lap_selected)

    def build_telemetry_tab(self):
        """Erstellt den Telemetrie-Tab"""
        tab = self.tab_view.tab("📈 Telemetrie")
        
        plot_container = ctk.CTkFrame(tab, fg_color=ColorPalette.BG_ELEVATED,
                                     corner_radius=10)
        plot_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.telemetry_tabs = ctk.CTkTabview(plot_container,
                                            fg_color="transparent",
                                            segmented_button_fg_color=ColorPalette.BG_CARD,
                                            segmented_button_selected_color=ColorPalette.ACCENT_BLUE)
        self.telemetry_tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.telemetry_tabs.add("🏎️ Speed")
        self.telemetry_tabs.add("⚡ Throttle/Brake")
        self.telemetry_tabs.add("🔧 RPM/Gear")
        
        self.telemetry_plots = {}
        for tab_name in ["🏎️ Speed", "⚡ Throttle/Brake", "🔧 RPM/Gear"]:
            fig = Figure(figsize=(8, 5), facecolor=ColorPalette.BG_CARD)
            ax = fig.add_subplot(111, facecolor=ColorPalette.BG_ELEVATED)
            canvas = FigureCanvasTkAgg(fig, master=self.telemetry_tabs.tab(tab_name))
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            self.telemetry_plots[tab_name] = {"fig": fig, "ax": ax, "canvas": canvas}
            self.style_plot(ax)

    def build_compare_tab(self):
        """Erstellt den Vergleichs-Tab"""
        tab = self.tab_view.tab("⚖️ Vergleich")
        
        controls = ctk.CTkFrame(tab, fg_color=ColorPalette.BG_ELEVATED,
                               corner_radius=10, height=100)
        controls.pack(fill="x", padx=10, pady=(10, 5))
        controls.pack_propagate(False)
        
        controls_inner = ctk.CTkFrame(controls, fg_color="transparent")
        controls_inner.pack(expand=True)
        
        ctk.CTkLabel(controls_inner, text="Fahrer 1:",
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=10, pady=5)
        self.compare_driver1 = ctk.CTkComboBox(controls_inner, width=150,
                                              fg_color=ColorPalette.BG_CARD,
                                              button_color=ColorPalette.F1_RED)
        self.compare_driver1.grid(row=1, column=0, padx=10, pady=5)
        
        ctk.CTkLabel(controls_inner, text="VS", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=ColorPalette.F1_RED).grid(row=1, column=1, padx=20)
        
        ctk.CTkLabel(controls_inner, text="Fahrer 2:",
                    font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=10, pady=5)
        self.compare_driver2 = ctk.CTkComboBox(controls_inner, width=150,
                                              fg_color=ColorPalette.BG_CARD,
                                              button_color=ColorPalette.ACCENT_BLUE)
        self.compare_driver2.grid(row=1, column=2, padx=10, pady=5)
        
        ctk.CTkButton(controls_inner, text="🔍 Vergleichen",
                     command=self.compare_drivers,
                     fg_color=ColorPalette.ACCENT_GREEN,
                     hover_color=ColorPalette.ACCENT_GREEN,
                     width=150, height=40,
                     font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=3, padx=20)
        
        plot_container = ctk.CTkFrame(tab, fg_color=ColorPalette.BG_ELEVATED,
                                     corner_radius=10)
        plot_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.compare_fig = Figure(figsize=(10, 6), facecolor=ColorPalette.BG_CARD)
        self.compare_ax = self.compare_fig.add_subplot(111, facecolor=ColorPalette.BG_ELEVATED)
        self.compare_canvas = FigureCanvasTkAgg(self.compare_fig, master=plot_container)
        self.compare_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        self.style_plot(self.compare_ax)

    def build_analysis_tab(self):
        """Erstellt den Analyse-Tab"""
        tab = self.tab_view.tab("🎯 Analyse")
        
        left = ctk.CTkFrame(tab, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        right = ctk.CTkFrame(tab, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Pace Analysis
        pace_frame = ctk.CTkFrame(left, fg_color=ColorPalette.BG_ELEVATED,
                                 corner_radius=10)
        pace_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        ctk.CTkLabel(pace_frame, text="📉 Pace-Analyse",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.pace_fig = Figure(figsize=(6, 4), facecolor=ColorPalette.BG_CARD)
        self.pace_ax = self.pace_fig.add_subplot(111, facecolor=ColorPalette.BG_ELEVATED)
        self.pace_canvas = FigureCanvasTkAgg(self.pace_fig, master=pace_frame)
        self.pace_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.style_plot(self.pace_ax)
        
        # Sector Analysis
        sector_frame = ctk.CTkFrame(right, fg_color=ColorPalette.BG_ELEVATED,
                                   corner_radius=10)
        sector_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        ctk.CTkLabel(sector_frame, text="🎯 Sektor-Analyse",
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.sector_fig = Figure(figsize=(6, 4), facecolor=ColorPalette.BG_CARD)
        self.sector_ax = self.sector_fig.add_subplot(111, facecolor=ColorPalette.BG_ELEVATED)
        self.sector_canvas = FigureCanvasTkAgg(self.sector_fig, master=sector_frame)
        self.sector_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self.style_plot(self.sector_ax)

    def style_plot(self, ax):
        """Stilisiert einen Matplotlib Axes"""
        ax.set_facecolor(ColorPalette.BG_ELEVATED)
        ax.tick_params(colors=ColorPalette.TEXT_PRIMARY, labelsize=9)
        ax.xaxis.label.set_color(ColorPalette.TEXT_PRIMARY)
        ax.yaxis.label.set_color(ColorPalette.TEXT_PRIMARY)
        ax.title.set_color(ColorPalette.TEXT_PRIMARY)
        
        for spine in ax.spines.values():
            spine.set_color(ColorPalette.BORDER)
        
        ax.grid(True, alpha=0.2, color=ColorPalette.BORDER, 
               linestyle='--', linewidth=0.5)

    # === DATA LOADING ===
    
    def load_years(self):
        """Lädt verfügbare Jahre"""
        years = list(range(1950, datetime.now().year + 1))
        years.reverse()
        self.year_cb.configure(values=[str(y) for y in years])
        default_year = years[0]
        if self.config and self.config.last_year in years:
            default_year = self.config.last_year
        self.year_var.set(str(default_year))
        self.on_year_selected()

    def on_year_selected(self, choice=None):
        """Jahr wurde ausgewählt"""
        if not self.year_var.get():
            return
        
        year = int(self.year_var.get())
        if self.config:
            self.config.last_year = year
            save_config(self.config)
        self.loading.show(f"📅 Lade Events für {year}...")
        
        def load_events():
            try:
                self.events = self.data_service.get_event_schedule(year)
                gps = [e['EventName'] for _, e in self.events.iterrows()]
                self.root.after(0, lambda: self.gp_cb.configure(values=gps))
                if self.config and self.config.last_event in gps and self.config.last_year == year:
                    self.root.after(0, lambda: self.gp_var.set(self.config.last_event))
                self.root.after(0, lambda: self.loading.hide())
            except Exception as e:
                self.root.after(0, lambda: self.show_error("Fehler beim Laden", str(e)))
                self.root.after(0, lambda: self.loading.hide())
        
        threading.Thread(target=load_events, daemon=True).start()

    def load_session(self):
        """Lädt eine Session"""
        if self.events is None:
            self.show_error("Fehler", "Bitte wählen Sie zuerst ein Jahr aus.")
            return
        
        year = int(self.year_var.get())
        gp_name = self.gp_var.get()
        ses = self.ses_var.get()
        if gp_name and ses and self.config:
            self.config.last_event = gp_name
            self.config.last_session = ses
            save_config(self.config)
        
        if not gp_name or not ses:
            self.show_error("Fehler", "Bitte wählen Sie einen Grand Prix und eine Session aus.")
            return
        
        self.loading.show(f"🏎️ Lade {year} {gp_name} {ses}...")
        self.load_btn.configure(state="disabled")
        
        def load_thread():
            try:
                event = self.events.loc[self.events['EventName'] == gp_name].iloc[0]
                session = self.data_service.get_session(year, event['EventName'], ses)
                
                self.root.after(0, lambda: self.loading.set_progress(0.3))
                session.load(telemetry=True, laps=True, messages=False)
                self.root.after(0, lambda: self.loading.set_progress(1.0))
                
                self.session = session
                self.root.after(0, self.on_session_loaded)
            except Exception as e:
                self.root.after(0, lambda: self.show_error("Ladefehler", str(e)))
                self.root.after(0, lambda: self.loading.hide())
                self.root.after(0, lambda: self.load_btn.configure(state="normal"))
        
        threading.Thread(target=load_thread, daemon=True).start()

    def on_session_loaded(self):
        """Callback wenn Session geladen wurde"""
        self.update_header()
        self.update_dashboard()
        self.fill_laps()
        self.update_compare_drivers()
        self.plot_pace_analysis()
        self.plot_sector_analysis()
        self.update_race_results()
        
        self.loading.hide()
        self.load_btn.configure(state="normal")

    # === STANDINGS & RESULTS ===
    
    def update_race_results(self):
        """Aktualisiert Race Results"""
        if not self.session:
            return
        
        try:
            def parse_position(value, fallback):
                if pd.isna(value):
                    return fallback
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return fallback

            # Check if it's a race session
            if self.ses_var.get() != 'R':
                # Show info message and clear
                self.race_info_label.pack(pady=20)
                self.results_table.delete(*self.results_table.get_children())
                self.podium.clear()
                return
            else:
                # Hide info message
                self.race_info_label.pack_forget()
            
            # Get results from session
            results = self.session.results
            
            # If no results object, try to construct from laps
            if results is None or results.empty:
                print("No results object, trying to construct from laps...")
                laps = self.session.laps
                if laps.empty:
                    self.podium.clear()
                    return
                
                # Get final positions from last lap
                final_laps = laps.groupby('Driver').last().reset_index()
                final_laps = final_laps.sort_values('Position')
                
                # Clear table
                self.results_table.delete(*self.results_table.get_children())
                self.podium.clear()
                
                # Fill table with lap data
                for idx, lap_data in final_laps.iterrows():
                    position = parse_position(lap_data.get('Position'), idx + 1)
                    driver = lap_data.get('Driver', '?')
                    team = lap_data.get('Team', '-')
                    
                    # Calculate points based on position
                    points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
                    points = points_map.get(position, 0)
                    
                    time_str = self.format_time(lap_data.get('LapTime', '—'))
                    
                    tags = []
                    if position == 1:
                        tags = ['p1']
                    elif position == 2:
                        tags = ['p2']
                    elif position == 3:
                        tags = ['p3']
                    
                    self.results_table.insert("", "end", values=(
                        position, driver, team, time_str, points, "Finished"
                    ), tags=tags)
                    
                    # Update podium
                    if position <= 3:
                        self.podium.set_position(position, driver, team, time_str, points)
                
                # Style
                self.results_table.tag_configure('p1', background=ColorPalette.GOLD, foreground="#000000")
                self.results_table.tag_configure('p2', background=ColorPalette.SILVER, foreground="#000000")
                self.results_table.tag_configure('p3', background=ColorPalette.BRONZE, foreground="#000000")
                return
            
            # Clear table
            self.results_table.delete(*self.results_table.get_children())
            self.podium.clear()
            
            # Podium (Top 3)
            for i in range(min(3, len(results))):
                result = results.iloc[i]
                position = i + 1
                
                # Get driver info
                driver = str(result.get('Abbreviation', result.get('DriverNumber', '?')))
                team = str(result.get('TeamName', '—'))
                
                # Time/Gap
                if position == 1:
                    time_val = result.get('Time')
                    if pd.notna(time_val):
                        time_str = self.format_time(time_val)
                    else:
                        time_str = "—"
                else:
                    time_val = result.get('Time')
                    winner_time = results.iloc[0].get('Time')
                    if pd.notna(time_val) and pd.notna(winner_time):
                        gap = time_val - winner_time
                        time_str = f"+{self.format_time(gap)}"
                    else:
                        time_str = "—"
                
                points = int(result.get('Points', 0))
                
                self.podium.set_position(position, driver, team, time_str, points)
            
            # Full results table
            for idx, result in results.iterrows():
                position = parse_position(result.get('Position'), idx + 1)
                driver = str(result.get('Abbreviation', result.get('DriverNumber', '?')))
                team = str(result.get('TeamName', '-'))
                
                if position == 1:
                    time_val = result.get('Time')
                    if pd.notna(time_val):
                        time_str = self.format_time(time_val)
                    else:
                        time_str = "—"
                else:
                    time_val = result.get('Time')
                    winner_time = results.iloc[0].get('Time')
                    if pd.notna(time_val) and pd.notna(winner_time):
                        gap = time_val - winner_time
                        time_str = f"+{self.format_time(gap)}"
                    else:
                        time_str = "—"
                
                points = int(result.get('Points', 0))
                status = str(result.get('Status', 'Finished'))
                
                # Color based on position
                tags = []
                if position == 1:
                    tags = ['p1']
                elif position == 2:
                    tags = ['p2']
                elif position == 3:
                    tags = ['p3']
                
                self.results_table.insert("", "end", values=(
                    position, driver, team, time_str, points, status
                ), tags=tags)
            
            # Style podium positions
            self.results_table.tag_configure('p1', background=ColorPalette.GOLD, foreground="#000000")
            self.results_table.tag_configure('p2', background=ColorPalette.SILVER, foreground="#000000")
            self.results_table.tag_configure('p3', background=ColorPalette.BRONZE, foreground="#000000")
            
        except Exception as e:
            print(f"Race Results Error: {e}")
            import traceback
            traceback.print_exc()

    def show_championship(self):
        """Zeigt Championship Standings"""
        if not self.year_var.get():
            self.show_error("Fehler", "Bitte wählen Sie zuerst ein Jahr aus.")
            return
        
        year = int(self.year_var.get())
        self.loading.show(f"🏆 Lade Championship {year}...")
        
        def load_championship():
            try:
                # Get event schedule for the year
                schedule = fastf1.get_event_schedule(year)
                
                # Driver standings
                driver_standings = {}
                constructor_standings = {}
                
                # Process each round
                for idx, event in schedule.iterrows():
                    try:
                        if event['EventFormat'] != 'conventional':
                            continue
                        
                        session = fastf1.get_session(year, event['EventName'], 'R')
                        session.load(laps=False, telemetry=False, weather=False, messages=False)
                        
                        if session.results is not None:
                            results = session.results
                            
                            # Update driver standings
                            for _, result in results.iterrows():
                                driver = result.get('Abbreviation', result.get('DriverNumber'))
                                points = result.get('Points', 0)
                                team = result.get('TeamName', '—')
                                
                                if driver not in driver_standings:
                                    driver_standings[driver] = {
                                        'points': 0,
                                        'wins': 0,
                                        'team': team
                                    }
                                
                                driver_standings[driver]['points'] += points
                                if result.get('Position') == 1:
                                    driver_standings[driver]['wins'] += 1
                                driver_standings[driver]['team'] = team
                                
                                # Constructor standings
                                if team not in constructor_standings:
                                    constructor_standings[team] = {'points': 0, 'wins': 0}
                                constructor_standings[team]['points'] += points
                                if result.get('Position') == 1:
                                    constructor_standings[team]['wins'] += 1
                    except:
                        continue
                
                self.root.after(0, lambda: self.display_championship(
                    driver_standings, constructor_standings
                ))
                self.root.after(0, lambda: self.loading.hide())
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error("Championship Error", str(e)))
                self.root.after(0, lambda: self.loading.hide())
        
        threading.Thread(target=load_championship, daemon=True).start()

    def display_championship(self, driver_standings, constructor_standings):
        """Zeigt Championship Daten an"""
        # Clear tables
        self.driver_standings_table.delete(*self.driver_standings_table.get_children())
        self.constructor_standings_table.delete(*self.constructor_standings_table.get_children())
        
        # Driver standings
        sorted_drivers = sorted(driver_standings.items(), 
                               key=lambda x: x[1]['points'], 
                               reverse=True)
        
        for pos, (driver, data) in enumerate(sorted_drivers, 1):
            tags = []
            if pos == 1:
                tags = ['p1']
            elif pos == 2:
                tags = ['p2']
            elif pos == 3:
                tags = ['p3']
            
            self.driver_standings_table.insert("", "end", values=(
                pos, driver, data['team'], int(data['points']), data['wins']
            ), tags=tags)
        
        # Constructor standings
        sorted_constructors = sorted(constructor_standings.items(),
                                    key=lambda x: x[1]['points'],
                                    reverse=True)
        
        for pos, (team, data) in enumerate(sorted_constructors, 1):
            tags = []
            if pos == 1:
                tags = ['p1']
            elif pos == 2:
                tags = ['p2']
            elif pos == 3:
                tags = ['p3']
            
            self.constructor_standings_table.insert("", "end", values=(
                pos, team, int(data['points']), data['wins']
            ), tags=tags)
        
        # Style
        for table in [self.driver_standings_table, self.constructor_standings_table]:
            table.tag_configure('p1', background=ColorPalette.GOLD)
            table.tag_configure('p2', background=ColorPalette.SILVER)
            table.tag_configure('p3', background=ColorPalette.BRONZE)
        
        # Plot driver points chart
        self.plot_driver_points(sorted_drivers[:10])  # Top 10
        
        # Plot constructor points chart
        self.plot_constructor_points(sorted_constructors[:10])  # Top 10
        
        # Switch to Standings tab
        self.tab_view.set("🏆 Standings")

    def plot_driver_points(self, sorted_drivers):
        """Plottet Fahrer-Punkte"""
        try:
            ax = self.driver_points_ax
            ax.clear()
            
            drivers = [d[0] for d in sorted_drivers]
            points = [d[1]['points'] for d in sorted_drivers]
            
            colors = [ColorPalette.GOLD if i == 0 else 
                     ColorPalette.SILVER if i == 1 else
                     ColorPalette.BRONZE if i == 2 else
                     ColorPalette.ACCENT_BLUE
                     for i in range(len(drivers))]
            
            bars = ax.barh(drivers, points, color=colors, alpha=0.8)
            
            # Add value labels
            for i, (bar, point) in enumerate(zip(bars, points)):
                ax.text(point + 5, i, f'{int(point)}', 
                       va='center', fontweight='bold',
                       color=ColorPalette.TEXT_PRIMARY)
            
            ax.set_xlabel('Punkte', color=ColorPalette.TEXT_PRIMARY)
            ax.set_title('Top 10 Fahrer', pad=15, fontweight='bold')
            ax.invert_yaxis()
            
            self.style_plot(ax)
            self.driver_points_canvas.draw()
            
        except Exception as e:
            print(f"Driver Points Plot Error: {e}")

    def plot_constructor_points(self, sorted_constructors):
        """Plottet Konstrukteur-Punkte"""
        try:
            ax = self.constructor_points_ax
            ax.clear()
            
            teams = [t[0] for t in sorted_constructors]
            points = [t[1]['points'] for t in sorted_constructors]
            
            # Get team colors
            colors = [TEAM_COLORS.get(team, ColorPalette.ACCENT_BLUE) 
                     for team in teams]
            
            bars = ax.barh(teams, points, color=colors, alpha=0.8)
            
            # Add value labels
            for i, (bar, point) in enumerate(zip(bars, points)):
                ax.text(point + 10, i, f'{int(point)}',
                       va='center', fontweight='bold',
                       color=ColorPalette.TEXT_PRIMARY)
            
            ax.set_xlabel('Punkte', color=ColorPalette.TEXT_PRIMARY)
            ax.set_title('Top 10 Teams', pad=15, fontweight='bold')
            ax.invert_yaxis()
            
            self.style_plot(ax)
            self.constructor_points_canvas.draw()
            
        except Exception as e:
            print(f"Constructor Points Plot Error: {e}")

    # === UI UPDATES ===
    
    def update_header(self):
        """Aktualisiert den Header"""
        if self.session:
            year = self.year_var.get()
            gp = self.gp_var.get()
            ses = self.ses_var.get()
            
            self.session_title.configure(text=f"{gp} {year}")
            self.session_subtitle.configure(text=f"Session: {ses}")

    def update_dashboard(self):
        """Aktualisiert die Dashboard-Karten"""
        if not self.session:
            return
        
        try:
            laps = self.session.laps
            valid_laps = laps[laps['LapTime'].notna()]
            
            if valid_laps.empty:
                return
            
            best_lap = valid_laps.nsmallest(1, 'LapTime').iloc[0]
            best_time = self.format_time(best_lap['LapTime'])
            fastest_driver = best_lap.get('Driver', '—')
            
            total_laps = len(valid_laps)
            total_drivers = len(laps['Driver'].unique())
            
            avg_speed = valid_laps['Speed'].mean() if 'Speed' in valid_laps.columns else 0
            
            best_sectors = []
            for col in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                if col in valid_laps.columns:
                    sector_valid = valid_laps[valid_laps[col].notna()]
                    if not sector_valid.empty:
                        best_sectors.append(sector_valid[col].min().total_seconds())
            
            best_sector_time = min(best_sectors) if best_sectors else 0
            
            self.stat_cards['best_time'].set_value(best_time, "Schnellste Runde")
            self.stat_cards['fastest_driver'].set_value(fastest_driver, "Pilot")
            self.stat_cards['total_laps'].set_value(total_laps, "Runden gesamt", animate=True)
            self.stat_cards['total_drivers'].set_value(total_drivers, "Teilnehmer", animate=True)
            self.stat_cards['avg_speed'].set_value(f"{avg_speed:.1f} km/h", "Durchschnitt")
            self.stat_cards['best_sector'].set_value(f"{best_sector_time:.3f}s", "Sektor")
            
        except Exception as e:
            print(f"Dashboard Update Error: {e}")

    def fill_laps(self):
        """Füllt die Laps-Tabelle"""
        self.lap_table.delete(*self.lap_table.get_children())
        
        if not self.session:
            return
        
        try:
            laps = self.session.laps.copy()
            
            if self.filter_text:
                laps = laps[
                    laps['Driver'].str.lower().str.contains(self.filter_text, na=False) |
                    laps['Team'].str.lower().str.contains(self.filter_text, na=False)
                ]
            
            sort_map = {
                "Pos": "Position",
                "Fahrer": "Driver",
                "Team": "Team",
                "Runde": "LapNumber",
                "Zeit": "LapTime",
                "S1": "Sector1Time",
                "S2": "Sector2Time",
                "S3": "Sector3Time",
                "Tempo": "Speed"
            }
            sort_key = sort_map.get(self.sort_column)
            if sort_key and sort_key in laps.columns:
                if sort_key in ["Position", "LapNumber", "Speed"]:
                    laps = laps.assign(_sort=pd.to_numeric(laps[sort_key], errors="coerce"))
                    laps = laps.sort_values(by="_sort",
                                            ascending=not self.sort_reverse,
                                            na_position='last').drop(columns=["_sort"])
                else:
                    laps = laps.sort_values(by=sort_key,
                                            ascending=not self.sort_reverse,
                                            na_position='last')
            else:
                laps = laps.sort_values(by='LapTime', ascending=True, na_position='last')
            
            fastest_laps = {}
            for driver in laps['Driver'].unique():
                driver_laps = laps[laps['Driver'] == driver]
                if not driver_laps.empty:
                    fastest = driver_laps.nsmallest(1, 'LapTime')
                    if not fastest.empty and pd.notna(fastest.iloc[0]['LapTime']):
                        fastest_laps[driver] = fastest.iloc[0]['LapTime']
            
            valid_laps = laps[laps['LapTime'].notna()]
            best_time = valid_laps['LapTime'].min() if not valid_laps.empty else None
            
            for idx, lap in laps.head(100).iterrows():
                pos = int(lap['Position']) if pd.notna(lap.get('Position')) else idx + 1
                driver = lap.get('Driver', '—')
                team = lap.get('Team', '—')
                lap_num = int(lap.get('LapNumber', 0))
                
                lap_time = self.format_time(lap.get('LapTime'))
                s1 = self.format_time(lap.get('Sector1Time'))
                s2 = self.format_time(lap.get('Sector2Time'))
                s3 = self.format_time(lap.get('Sector3Time'))
                speed = f"{lap.get('Speed', 0):.1f}" if pd.notna(lap.get('Speed')) else '—'
                
                is_best = ""
                if driver in fastest_laps and pd.notna(lap.get('LapTime')):
                    if lap['LapTime'] == fastest_laps[driver]:
                        is_best = "⭐"
                
                tags = []
                if best_time is not None and pd.notna(lap.get('LapTime')):
                    if lap['LapTime'] == best_time:
                        tags = ['fastest']
                
                iid = f"{driver}_{lap_num}"
                self.lap_table.insert("", "end", iid=iid, tags=tags,
                                     values=(pos, driver, team, lap_num, lap_time,
                                            s1, s2, s3, speed, is_best))
            
            self.lap_table.tag_configure('fastest', 
                                        background=ColorPalette.SUCCESS,
                                        foreground=ColorPalette.TEXT_PRIMARY)
            
        except Exception as e:
            print(f"Fill Laps Error: {e}")

    def update_compare_drivers(self):
        """Aktualisiert die Fahrer-Auswahl für Vergleich"""
        if not self.session:
            return
        
        drivers = sorted({d for d in self.session.laps['Driver'] if pd.notna(d)})
        self.compare_driver1.configure(values=drivers)
        self.compare_driver2.configure(values=drivers)

    # === PLOTS ===
    
    def plot_lap_telemetry(self, lap):
        """Plottet Telemetrie für eine Runde"""
        try:
            tel = lap.get_car_data().add_distance()
            if tel is None or tel.empty:
                return
            
            dist = tel['Distance']
            driver = lap.get('Driver', 'Unknown')
            lap_num = lap.get('LapNumber', '?')
            
            # Speed
            plot = self.telemetry_plots["🏎️ Speed"]
            ax = plot['ax']
            ax.clear()
            
            ax.plot(dist, tel['Speed'], color=ColorPalette.F1_RED, linewidth=2.5)
            ax.fill_between(dist, tel['Speed'], alpha=0.3, color=ColorPalette.F1_RED)
            ax.set_xlabel('Distanz (m)')
            ax.set_ylabel('Geschwindigkeit (km/h)')
            ax.set_title(f'{driver} - Runde {lap_num}', pad=15, fontweight='bold')
            
            self.style_plot(ax)
            plot['canvas'].draw()
            
            # Throttle/Brake
            if 'Throttle' in tel.columns and 'Brake' in tel.columns:
                plot = self.telemetry_plots["⚡ Throttle/Brake"]
                ax = plot['ax']
                ax.clear()
                
                ax.plot(dist, tel['Throttle'] * 100, color=ColorPalette.ACCENT_GREEN, 
                       linewidth=2, label='Gas', alpha=0.8)
                ax.plot(dist, tel['Brake'] * 100, color=ColorPalette.ERROR, 
                       linewidth=2, label='Bremse', alpha=0.8)
                ax.fill_between(dist, tel['Throttle'] * 100, alpha=0.2, 
                               color=ColorPalette.ACCENT_GREEN)
                ax.fill_between(dist, tel['Brake'] * 100, alpha=0.2, 
                               color=ColorPalette.ERROR)
                
                ax.set_xlabel('Distanz (m)')
                ax.set_ylabel('Prozent (%)')
                ax.set_title('Gas & Bremse', pad=15, fontweight='bold')
                ax.legend(loc='upper right')
                ax.set_ylim(0, 105)
                
                self.style_plot(ax)
                plot['canvas'].draw()
            
            # RPM/Gear
            if 'RPM' in tel.columns:
                plot = self.telemetry_plots["🔧 RPM/Gear"]
                ax = plot['ax']
                ax.clear()
                
                color = ColorPalette.ACCENT_ORANGE
                ax.plot(dist, tel['RPM'], color=color, linewidth=2.5, label='RPM')
                ax.fill_between(dist, tel['RPM'], alpha=0.3, color=color)
                ax.set_xlabel('Distanz (m)')
                ax.set_ylabel('RPM')
                ax.set_title('Motor & Getriebe', pad=15, fontweight='bold')
                
                if 'nGear' in tel.columns:
                    ax2 = ax.twinx()
                    ax2.plot(dist, tel['nGear'], color=ColorPalette.ACCENT_BLUE,
                            linewidth=2, alpha=0.8, linestyle='--', label='Gang')
                    ax2.set_ylabel('Gang', color=ColorPalette.ACCENT_BLUE)
                    ax2.tick_params(colors=ColorPalette.ACCENT_BLUE)
                    ax2.set_ylim(0.5, 8.5)
                
                self.style_plot(ax)
                ax.tick_params(colors=color)
                ax.yaxis.label.set_color(color)
                plot['canvas'].draw()
            
        except Exception as e:
            print(f"Telemetry Plot Error: {e}")

    def compare_drivers(self):
        """Vergleicht zwei Fahrer"""
        if not self.session:
            return
        
        driver1 = self.compare_driver1.get()
        driver2 = self.compare_driver2.get()
        
        if not driver1 or not driver2 or driver1 == driver2:
            return
        
        try:
            laps1 = self.session.laps.pick_drivers(driver1)
            laps2 = self.session.laps.pick_drivers(driver2)
            
            if laps1.empty or laps2.empty:
                return
            
            lap1 = laps1.pick_fastest()
            lap2 = laps2.pick_fastest()
            
            tel1 = lap1.get_car_data().add_distance()
            tel2 = lap2.get_car_data().add_distance()
            
            if tel1 is None or tel1.empty or tel2 is None or tel2.empty:
                return
            
            ax = self.compare_ax
            ax.clear()
            
            ax.plot(tel1['Distance'], tel1['Speed'], 
                   color=ColorPalette.F1_RED, linewidth=2.5,
                   label=f"{driver1} ({self.format_time(lap1['LapTime'])})", alpha=0.9)
            ax.plot(tel2['Distance'], tel2['Speed'], 
                   color=ColorPalette.ACCENT_BLUE, linewidth=2.5,
                   label=f"{driver2} ({self.format_time(lap2['LapTime'])})", alpha=0.9)
            
            ax.fill_between(tel1['Distance'], tel1['Speed'], 
                           alpha=0.2, color=ColorPalette.F1_RED)
            ax.fill_between(tel2['Distance'], tel2['Speed'], 
                           alpha=0.2, color=ColorPalette.ACCENT_BLUE)
            
            ax.set_xlabel('Distanz (m)')
            ax.set_ylabel('Geschwindigkeit (km/h)')
            ax.set_title(f'{driver1} vs {driver2}', pad=15, fontweight='bold', fontsize=14)
            ax.legend(loc='upper right', fontsize=11)
            
            self.style_plot(ax)
            self.compare_canvas.draw()
            
        except Exception as e:
            print(f"Compare Error: {e}")

    def plot_pace_analysis(self):
        """Plottet Pace-Analyse"""
        if not self.session:
            return
        
        try:
            laps = self.session.laps
            valid_laps = laps[laps['LapTime'].notna()]
            
            if valid_laps.empty:
                return
            
            ax = self.pace_ax
            ax.clear()
            
            drivers = valid_laps['Driver'].unique()[:10]
            colors = plt.cm.rainbow(np.linspace(0, 1, len(drivers)))
            
            for i, driver in enumerate(drivers):
                driver_laps = valid_laps[valid_laps['Driver'] == driver]
                lap_times = [t.total_seconds() for t in driver_laps['LapTime']]
                lap_nums = driver_laps['LapNumber'].tolist()
                
                ax.plot(lap_nums, lap_times, marker='o', markersize=4,
                       linewidth=2, label=driver, color=colors[i], alpha=0.7)
            
            ax.set_xlabel('Rundennummer')
            ax.set_ylabel('Rundenzeit (Sekunden)')
            ax.set_title('Pace-Entwicklung', pad=15, fontweight='bold')
            ax.legend(loc='upper right', fontsize=8, ncol=2)
            
            self.style_plot(ax)
            self.pace_canvas.draw()
            
        except Exception as e:
            print(f"Pace Analysis Error: {e}")

    def plot_sector_analysis(self):
        """Plottet Sektor-Analyse"""
        if not self.session:
            return
        
        try:
            def min_sector_time(df, column):
                if column not in df.columns:
                    return 0
                values = df[column].dropna()
                if values.empty:
                    return 0
                min_val = values.min()
                if hasattr(min_val, "total_seconds"):
                    return min_val.total_seconds()
                try:
                    return float(min_val)
                except (TypeError, ValueError):
                    return 0

            laps = self.session.laps
            valid_laps = laps[laps['LapTime'].notna()]
            
            if valid_laps.empty:
                return
            
            ax = self.sector_ax
            ax.clear()
            
            drivers = sorted(valid_laps['Driver'].unique())[:10]
            s1_times = []
            s2_times = []
            s3_times = []
            
            for driver in drivers:
                driver_laps = valid_laps[valid_laps['Driver'] == driver]
                s1 = min_sector_time(driver_laps, 'Sector1Time')
                s2 = min_sector_time(driver_laps, 'Sector2Time')
                s3 = min_sector_time(driver_laps, 'Sector3Time')
                
                s1_times.append(s1)
                s2_times.append(s2)
                s3_times.append(s3)
            
            x = np.arange(len(drivers))
            width = 0.25
            
            ax.bar(x - width, s1_times, width, label='Sektor 1', 
                  color=ColorPalette.F1_RED, alpha=0.8)
            ax.bar(x, s2_times, width, label='Sektor 2', 
                  color=ColorPalette.ACCENT_BLUE, alpha=0.8)
            ax.bar(x + width, s3_times, width, label='Sektor 3', 
                  color=ColorPalette.ACCENT_GREEN, alpha=0.8)
            
            ax.set_xlabel('Fahrer')
            ax.set_ylabel('Zeit (Sekunden)')
            ax.set_title('Beste Sektorzeiten', pad=15, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(drivers, rotation=45, ha='right')
            ax.legend(loc='upper right')
            
            self.style_plot(ax)
            self.sector_canvas.draw()
            
        except Exception as e:
            print(f"Sector Analysis Error: {e}")

    # === EVENTS ===
    
    def on_lap_selected(self, event):
        """Runde wurde in Tabelle ausgewählt"""
        if not self.session:
            return
        
        sel = self.lap_table.selection()
        if not sel:
            return
        
        try:
            iid = sel[0]
            driver, lapnum = iid.rsplit("_", 1)
            lapnum = int(float(lapnum))
            
            lap = self.session.laps[
                (self.session.laps['Driver'] == driver) & 
                (self.session.laps['LapNumber'] == lapnum)
            ]
            
            if lap.empty:
                return
            
            lap = lap.iloc[0]
            self.plot_lap_telemetry(lap)
            
        except Exception as e:
            print(f"Lap Selection Error: {e}")

    def on_search_changed(self, event=None):
        """Suche wurde geändert"""
        self.filter_text = self.search_entry.get().lower()
        self.fill_laps()

    def sort_table(self, column):
        """Sortiert Tabelle nach Spalte"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.fill_laps()

    # === ACTIONS ===
    
    def export_data(self):
        """Exportiert Daten"""
        if not self.session:
            self.show_error("Fehler", "Keine Session geladen.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), 
                      ("Excel files", "*.xlsx"), 
                      ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            data = []
            for item in self.lap_table.get_children():
                values = self.lap_table.item(item, 'values')
                data.append({
                    'Position': values[0],
                    'Fahrer': values[1],
                    'Team': values[2],
                    'Runde': values[3],
                    'Zeit': values[4],
                    'Sektor 1': values[5],
                    'Sektor 2': values[6],
                    'Sektor 3': values[7],
                    'Tempo': values[8],
                    'Best': values[9]
                })
            
            df = pd.DataFrame(data)
            
            if filename.endswith('.xlsx'):
                df.to_excel(filename, index=False)
            else:
                df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo("Erfolg", f"Daten exportiert nach:\n{filename}")
            
        except Exception as e:
            self.show_error("Export Fehler", str(e))

    def export_plot(self):
        """Exportiert Charts"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), 
                      ("PDF files", "*.pdf"), 
                      ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.pdf'):
                from matplotlib.backends.backend_pdf import PdfPages
                with PdfPages(filename) as pdf:
                    for plot_dict in self.telemetry_plots.values():
                        pdf.savefig(plot_dict['fig'], bbox_inches='tight')
                    pdf.savefig(self.compare_fig, bbox_inches='tight')
                    pdf.savefig(self.pace_fig, bbox_inches='tight')
                    pdf.savefig(self.sector_fig, bbox_inches='tight')
            else:
                first_plot = list(self.telemetry_plots.values())[0]
                first_plot['fig'].savefig(filename, dpi=300, bbox_inches='tight')
            
            messagebox.showinfo("Erfolg", f"Charts exportiert nach:\n{filename}")
            
        except Exception as e:
            self.show_error("Export Fehler", str(e))

    def reset_view(self):
        """Setzt Ansicht zurück"""
        self.search_entry.delete(0, 'end')
        self.filter_text = ""
        self.sort_column = None
        self.sort_reverse = False
        if self.session:
            self.fill_laps()

    # === UTILITIES ===
    
    def format_time(self, time_val):
        """Formatiert Zeitwerte"""
        if pd.isna(time_val) or time_val is None:
            return "—"
        try:
            if hasattr(time_val, 'total_seconds'):
                total_seconds = time_val.total_seconds()
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                if minutes > 0:
                    return f"{minutes}:{seconds:06.3f}"
                return f"{seconds:.3f}"
            return str(time_val)
        except:
            return str(time_val)

    def show_error(self, title, message):
        """Zeigt Fehlermeldung"""
        if self.logger:
            try:
                self.logger.error("%s: %s", title, message)
            except Exception:
                pass
        messagebox.showerror(title, message)
        self.loading.hide()


def main():
    if not check_dependencies():
        sys.exit(1)

    config = load_config()
    app_data_dir = get_app_data_dir()
    logger = setup_logging(app_data_dir)
    logger.info("Starting F1 Desktop Pro")

    if config.theme:
        ctk.set_appearance_mode(config.theme)
    ctk.set_default_color_theme("blue")

    cache_dir = config.cache_dir or str(app_data_dir / "cache")
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

    if not ensure_license(config):
        sys.exit(1)

    root = ctk.CTk()
    app = F1DesktopPro(root, config=config, logger=logger)
    root.mainloop()


if __name__ == "__main__":
    main()
