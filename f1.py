"""
F1 Desktop App (CustomTkinter Version) — FastF1 (Automatisch)

Benötigt:
    pip install fastf1 matplotlib pandas numpy customtkinter
    
Optional (für Fahrervergleich):
    pip install scipy
    
Optional (für Excel-Export):
    pip install openpyxl

Starten:
    python f1.py

Features:
- Automatisches Laden aller verfügbaren Jahre und Grand Prix
- Dashboard mit Session-Übersicht (Beste Zeit, Schnellster Fahrer, etc.)
- Detaillierte Rundenzeiten-Tabelle mit Position, Team, Sektoren, Geschwindigkeit
- Erweiterte Telemetrie-Visualisierung:
  * Geschwindigkeit über Strecke
  * Gas & Bremse
  * RPM & Gänge
- Fahrervergleichsfunktion
- Moderne UI mit CustomTkinter
- Loading-States während Datenladen
- Tooltips für bessere Benutzerführung
- Export-Funktionen (CSV, Excel, PNG)
- Verbesserte Tabellen mit Sortierung und Filter
"""

import fastf1
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog

import os
import threading
from datetime import datetime

# --- Cache automatisch erstellen ---
cache_dir = ".fastf1_cache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# CustomTkinter Theme konfigurieren
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ToolTip:
    """Einfaches Tooltip-Widget für CustomTkinter"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Segoe UI", 9))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class F1TkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏎️ F1 Desktop – FastF1 (Automatisch)")
        self.root.geometry("1400x800")
        self.session = None
        self.events = None
        self.current_lap = None
        self.sort_column = None
        self.sort_reverse = False
        self.filter_text = ""

        # F1 Rot als Akzentfarbe
        self.accent_color = "#e10600"
        
        self.build_ui()
        self.load_years()

    # -----------------------------------------------------
    def build_ui(self):
        # Hauptcontainer
        main_container = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header Frame
        header = ctk.CTkFrame(main_container, fg_color=("gray85", "gray17"))
        header.pack(fill="x", padx=10, pady=10)

        title_label = ctk.CTkLabel(header, text="🏎️ F1 Datenanalyse", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Control Panel
        control_panel = ctk.CTkFrame(header, fg_color="transparent")
        control_panel.pack(fill="x", padx=15, pady=10)

        # Jahr Dropdown
        year_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        year_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(year_frame, text="Jahr:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        self.year_var = ctk.StringVar()
        self.year_cb = ctk.CTkComboBox(year_frame, variable=self.year_var, 
                                      width=120, state="readonly",
                                      command=self.on_year_selected)
        self.year_cb.pack()
        ToolTip(self.year_cb, "Wählen Sie das Jahr des Grand Prix")

        # GP Dropdown
        gp_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        gp_frame.pack(side="left", padx=(0, 15), fill="x", expand=True)
        ctk.CTkLabel(gp_frame, text="Grand Prix:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        self.gp_var = ctk.StringVar()
        self.gp_cb = ctk.CTkComboBox(gp_frame, variable=self.gp_var, 
                                    width=300, state="readonly")
        self.gp_cb.pack(fill="x")
        ToolTip(self.gp_cb, "Wählen Sie den Grand Prix")

        # Session Dropdown
        session_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        session_frame.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(session_frame, text="Session:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        self.ses_var = ctk.StringVar()
        self.ses_cb = ctk.CTkComboBox(session_frame, variable=self.ses_var,
                                     values=["FP1", "FP2", "FP3", "Q", "R", "Q1", "Q2", "Q3"],
                                     width=100, state="readonly")
        self.ses_cb.pack()
        ToolTip(self.ses_cb, "Wählen Sie die Session (FP=Free Practice, Q=Qualifying, R=Race)")

        # Load Button
        button_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        button_frame.pack(side="left", padx=(15, 0))
        ctk.CTkLabel(button_frame, text="", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 5))
        self.load_btn = ctk.CTkButton(button_frame, text="📥 Laden", 
                                      command=self.load_session,
                                      fg_color=self.accent_color,
                                      hover_color="#ff1a1a",
                                      width=120, height=32)
        self.load_btn.pack()
        ToolTip(self.load_btn, "Lädt die ausgewählte Session")

        # Status Label und Progress Bar
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(status_frame, text="Bereit", 
                                        font=ctk.CTkFont(size=11),
                                        text_color=("gray50", "gray50"))
        self.status_label.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200, height=10)
        self.progress_bar.pack(side="right", padx=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Versteckt initial

        # Export Button
        export_btn = ctk.CTkButton(status_frame, text="💾 Export", 
                                   command=self.export_data,
                                   width=100, height=28,
                                   fg_color=("gray70", "gray30"))
        export_btn.pack(side="right", padx=(10, 0))
        ToolTip(export_btn, "Exportiert Tabellendaten als CSV/Excel")

        # --- Dashboard Bereich (Session Übersicht) ---
        dashboard_frame = ctk.CTkFrame(main_container, fg_color=("gray85", "gray17"))
        dashboard_frame.pack(fill="x", padx=10, pady=(0, 10))

        dashboard_inner = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        dashboard_inner.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(dashboard_inner, text="📈 Session-Übersicht", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))

        stats_container = ctk.CTkFrame(dashboard_inner, fg_color="transparent")
        stats_container.pack(fill="x")

        # Statistik Labels
        self.stat_labels = {}
        stat_items = [
            ("Beste Zeit", "best_time"),
            ("Schnellster Fahrer", "fastest_driver"),
            ("Anzahl Runden", "total_laps"),
            ("Anzahl Fahrer", "total_drivers"),
            ("Session-Typ", "session_type")
        ]

        for i, (label, key) in enumerate(stat_items):
            frame = ctk.CTkFrame(stats_container, fg_color="transparent")
            frame.pack(side="left", padx=20, fill="x", expand=True)
            ctk.CTkLabel(frame, text=label + ":", 
                       font=ctk.CTkFont(size=10),
                       text_color=("gray50", "gray50")).pack(anchor="w")
            value_label = ctk.CTkLabel(frame, text="—", 
                                     font=ctk.CTkFont(size=12, weight="bold"))
            value_label.pack(anchor="w")
            self.stat_labels[key] = value_label

        # --- Main Content Area ---
        main = ctk.CTkFrame(main_container, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- Links: Runden Tabelle ---
        left_container = ctk.CTkFrame(main, fg_color="transparent")
        left_container.pack(side="left", fill="both", expand=True, padx=(0, 5))

        left_header = ctk.CTkFrame(left_container, fg_color=("gray85", "gray17"))
        left_header.pack(fill="x", pady=(0, 10))

        header_inner = ctk.CTkFrame(left_header, fg_color="transparent")
        header_inner.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header_inner, text="⏱️ Rundenzeiten", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        # Filter Input
        filter_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        filter_frame.pack(side="right")
        ctk.CTkLabel(filter_frame, text="Filter:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(0, 5))
        self.filter_entry = ctk.CTkEntry(filter_frame, width=150, height=28,
                                        placeholder_text="Fahrer, Team...")
        self.filter_entry.pack(side="left")
        self.filter_entry.bind("<KeyRelease>", self.on_filter_changed)
        ToolTip(self.filter_entry, "Filtern Sie die Tabelle nach Fahrer oder Team")

        left = ctk.CTkFrame(left_container, fg_color=("gray90", "gray10"))
        left.pack(fill="both", expand=True)

        # Tabelle mit Scrollbar
        table_frame = ctk.CTkFrame(left, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Verwende tkinter Treeview für bessere Funktionalität
        from tkinter import ttk as tk_ttk
        
        scrollbar_y = tk.Scrollbar(table_frame, orient="vertical", 
                                   bg="#2b2b2b", troughcolor="#1a1a1a",
                                   activebackground="#3d3d3d")
        scrollbar_x = tk.Scrollbar(table_frame, orient="horizontal",
                                   bg="#2b2b2b", troughcolor="#1a1a1a",
                                   activebackground="#3d3d3d")

        self.lap_table = tk_ttk.Treeview(
            table_frame,
            columns=("Pos", "Fahrer", "Team", "Runde", "Rundenzeit", "S1", "S2", "S3", "Ø Geschw.", "Beste"),
            show="headings",
            height=20,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            style="Custom.Treeview"
        )

        # Style für Treeview - Dark Theme Farben
        style = tk_ttk.Style()
        style.theme_use("clam")
        # Dark Theme Farben
        style.configure("Custom.Treeview",
                       background="#2b2b2b",  # Dunkler Hintergrund
                       foreground="#ffffff",  # Weißer Text
                       fieldbackground="#2b2b2b",
                       borderwidth=0,
                       rowheight=25)
        style.configure("Custom.Treeview.Heading",
                       background="#3d3d3d",  # Etwas hellerer Hintergrund für Header
                       foreground="#ffffff",  # Weißer Text
                       borderwidth=1,
                       relief="flat")
        style.map("Custom.Treeview",
                 background=[("selected", self.accent_color)],
                 foreground=[("selected", "#ffffff")])

        scrollbar_y.config(command=self.lap_table.yview)
        scrollbar_x.config(command=self.lap_table.xview)

        # Spalten konfigurieren
        col_widths = {
            "Pos": 50, "Fahrer": 100, "Team": 100, "Runde": 60,
            "Rundenzeit": 100, "S1": 80, "S2": 80, "S3": 80,
            "Ø Geschw.": 90, "Beste": 60
        }
        columns = ("Pos", "Fahrer", "Team", "Runde", "Rundenzeit", "S1", "S2", "S3", "Ø Geschw.", "Beste")
        for col in columns:
            self.lap_table.heading(col, text=col, command=lambda c=col: self.sort_table(c))
            self.lap_table.column(col, width=col_widths.get(col, 100), anchor="center")
            ToolTip(self.lap_table, f"Klicken Sie auf '{col}' zum Sortieren")

        self.lap_table.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.lap_table.bind("<<TreeviewSelect>>", self.on_lap_selected)

        # --- Rechts: Telemetrie Plot ---
        right_container = ctk.CTkFrame(main, fg_color="transparent")
        right_container.pack(side="right", fill="both", expand=True, padx=(5, 0))

        right_header = ctk.CTkFrame(right_container, fg_color=("gray85", "gray17"))
        right_header.pack(fill="x", pady=(0, 10))

        header_inner_right = ctk.CTkFrame(right_header, fg_color="transparent")
        header_inner_right.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header_inner_right, text="📊 Telemetrie", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        # Export Plot Button
        export_plot_btn = ctk.CTkButton(header_inner_right, text="💾 Plot exportieren",
                                        command=self.export_plot,
                                        width=140, height=28,
                                        fg_color=("gray70", "gray30"))
        export_plot_btn.pack(side="right")
        ToolTip(export_plot_btn, "Exportiert die aktuelle Grafik als PNG")

        right = ctk.CTkFrame(right_container, fg_color=("gray90", "gray10"))
        right.pack(fill="both", expand=True)

        # Plot Frame mit Tabs
        plot_tabview = ctk.CTkTabview(right)
        plot_tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Bestimme Plot-Farben basierend auf Theme
        self.plot_bg_color = "#1a1a1a"  # Dark theme default
        self.plot_text_color = "#ffffff"
        self.plot_border_color = "#4d4d4d"
        
        # Tab 1: Geschwindigkeit
        speed_frame = plot_tabview.add("🚗 Geschwindigkeit")
        self.fig = Figure(figsize=(6, 4), facecolor=self.plot_bg_color)
        self.ax = self.fig.add_subplot(111, facecolor=self.plot_bg_color)

        # Tab 2: Gas & Bremse
        throttle_frame = plot_tabview.add("⚡ Gas & Bremse")
        self.fig2 = Figure(figsize=(6, 4), facecolor=self.plot_bg_color)
        self.ax2 = self.fig2.add_subplot(111, facecolor=self.plot_bg_color)

        # Tab 3: RPM & Gänge
        rpm_frame = plot_tabview.add("🔧 RPM & Gänge")
        self.fig3 = Figure(figsize=(6, 4), facecolor=self.plot_bg_color)
        self.ax3 = self.fig3.add_subplot(111, facecolor=self.plot_bg_color)

        # Tab 4: Vergleich
        compare_frame = plot_tabview.add("⚖️ Vergleich")
        self.fig4 = Figure(figsize=(6, 4), facecolor=self.plot_bg_color)
        self.ax4 = self.fig4.add_subplot(111, facecolor=self.plot_bg_color)

        # Canvas für alle Tabs
        self.canvas = FigureCanvasTkAgg(self.fig, master=speed_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=throttle_frame)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)

        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=rpm_frame)
        self.canvas3.get_tk_widget().pack(fill="both", expand=True)

        self.canvas4 = FigureCanvasTkAgg(self.fig4, master=compare_frame)
        self.canvas4.get_tk_widget().pack(fill="both", expand=True)

        # Initialisiere alle Plots
        self.init_plots()

        # Fahrer Auswahl Bereich
        driver_frame = ctk.CTkFrame(right, fg_color=("gray85", "gray17"))
        driver_frame.pack(fill="x", padx=10, pady=(0, 10))

        driver_header = ctk.CTkFrame(driver_frame, fg_color="transparent")
        driver_header.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(driver_header, text="👤 Fahrer auswählen", 
                    font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkLabel(driver_header, text="(Doppelklick für beste Runde)",
                    font=ctk.CTkFont(size=10),
                    text_color=("gray50", "gray50")).pack(side="left", padx=(10, 0))

        # Scrollable Frame für Fahrerliste
        self.driver_scroll = ctk.CTkScrollableFrame(driver_frame, height=120)
        self.driver_scroll.pack(fill="x", padx=10, pady=(0, 10))
        self.driver_buttons = []

        # Vergleichsfunktion
        compare_frame_ui = ctk.CTkFrame(driver_frame, fg_color="transparent")
        compare_frame_ui.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(compare_frame_ui, text="⚖️ Fahrer vergleichen:",
                    font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 10))

        self.compare_driver1 = ctk.CTkComboBox(compare_frame_ui, state="readonly", width=120)
        self.compare_driver1.pack(side="left", padx=(0, 5))
        ToolTip(self.compare_driver1, "Wählen Sie den ersten Fahrer zum Vergleichen")

        self.compare_driver2 = ctk.CTkComboBox(compare_frame_ui, state="readonly", width=120)
        self.compare_driver2.pack(side="left", padx=(0, 5))
        ToolTip(self.compare_driver2, "Wählen Sie den zweiten Fahrer zum Vergleichen")

        compare_btn = ctk.CTkButton(compare_frame_ui, text="Vergleichen",
                                   command=self.compare_drivers,
                                   fg_color=self.accent_color,
                                   hover_color="#ff1a1a",
                                   width=100)
        compare_btn.pack(side="left")
        ToolTip(compare_btn, "Vergleicht die besten Runden der beiden Fahrer")

    # -----------------------------------------------------
    def init_plots(self):
        """Initialisiert alle Plots mit Platzhalter-Text"""
        text_color = self.plot_text_color
        bg_color = self.plot_bg_color
        border_color = self.plot_border_color

        for ax in [self.ax, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor(bg_color)
            ax.tick_params(colors=text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.title.set_color(text_color)
            for spine in ax.spines.values():
                spine.set_color(border_color)
            ax.grid(True, alpha=0.2, color=border_color, linestyle='--', linewidth=0.5)
            ax.text(0.5, 0.5, 'Wähle eine Runde aus,\num Daten zu sehen',
                   transform=ax.transAxes,
                   ha='center', va='center',
                   fontsize=12, color=text_color,
                   style='italic')
            ax.set_xticks([])
            ax.set_yticks([])

        self.ax.text(0.5, 0.5, 'Wähle eine Session aus,\num Telemetriedaten zu laden',
                    transform=self.ax.transAxes,
                    ha='center', va='center',
                    fontsize=12, color=text_color,
                    style='italic')

        for fig in [self.fig, self.fig2, self.fig3, self.fig4]:
            fig.patch.set_facecolor(bg_color)

    # -----------------------------------------------------
    def load_years(self):
        from datetime import datetime
        years = list(range(1950, datetime.now().year + 1))
        years.reverse()
        # Konvertiere zu Strings für CustomTkinter
        self.year_cb.configure(values=[str(y) for y in years])

    # -----------------------------------------------------
    def on_year_selected(self, choice=None):
        if not self.year_var.get():
            return
        year = int(self.year_var.get())
        self.update_status(f"Lade Events für {year}...")
        try:
            self.events = fastf1.get_event_schedule(year)
            gps = [e['EventName'] for _, e in self.events.iterrows()]
            self.gp_cb.configure(values=gps)
            self.update_status(f"{len(gps)} Grand Prix gefunden")
        except Exception as e:
            messagebox.showerror("Fehler beim Laden der Events", str(e))
            self.update_status("Fehler beim Laden")

    # -----------------------------------------------------
    def load_session(self):
        if self.events is None:
            messagebox.showerror("Fehler", "Bitte wählen Sie zuerst ein Jahr aus.")
            return

        year = int(self.year_var.get())
        gp_name = self.gp_var.get()
        ses = self.ses_var.get()

        if not gp_name or not ses:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Grand Prix und eine Session aus.")
            return

        # Deaktiviere Button während Laden
        self.load_btn.configure(state="disabled")
        self.progress_bar.pack(side="right", padx=(10, 0))
        self.progress_bar.set(0)
        self.update_status(f"Lade Session {year} {gp_name} {ses}...")

        # Lade in separatem Thread
        def load_thread():
            try:
                event = self.events.loc[self.events['EventName'] == gp_name].iloc[0]
                session = fastf1.get_session(year, event['EventName'], ses)
                
                # Simuliere Progress
                self.root.after(0, lambda: self.progress_bar.set(0.3))
                session.load(telemetry=True, laps=True, messages=True)
                self.root.after(0, lambda: self.progress_bar.set(1.0))
                
                self.session = session
                self.root.after(0, self.on_session_loaded)
            except Exception as e:
                self.root.after(0, lambda: self.on_load_error(str(e)))

        threading.Thread(target=load_thread, daemon=True).start()

    # -----------------------------------------------------
    def on_session_loaded(self):
        self.fill_laps()
        self.fill_drivers()
        self.progress_bar.pack_forget()
        self.load_btn.configure(state="normal")
        self.update_status("Session geladen")

    # -----------------------------------------------------
    def on_load_error(self, error_msg):
        messagebox.showerror("Fehler beim Laden", f"Die Session konnte nicht geladen werden:\n{error_msg}")
        self.progress_bar.pack_forget()
        self.load_btn.configure(state="normal")
        self.update_status("Fehler beim Laden")

    # -----------------------------------------------------
    def update_status(self, message):
        self.status_label.configure(text=message)

    # -----------------------------------------------------
    def update_dashboard(self):
        """Aktualisiert das Dashboard mit Session-Statistiken"""
        if self.session is None:
            for key in self.stat_labels:
                self.stat_labels[key].configure(text="—")
            return

        try:
            laps = self.session.laps

            # Beste Zeit
            valid_laps = laps[laps['LapTime'].notna()]
            if not valid_laps.empty:
                best_lap = valid_laps.nsmallest(1, 'LapTime').iloc[0]
                best_time = self.format_time(best_lap['LapTime'])
                fastest_driver = best_lap.get('Driver', '—')
            else:
                best_time = "—"
                fastest_driver = "—"

            # Anzahl Runden
            total_laps = len(laps[laps['LapTime'].notna()])

            # Anzahl Fahrer
            total_drivers = len(laps['Driver'].unique()) if not laps.empty else 0

            # Session Typ
            session_type = self.ses_var.get() if self.ses_var.get() else "—"

            # Update Labels
            self.stat_labels['best_time'].configure(text=best_time)
            self.stat_labels['fastest_driver'].configure(text=fastest_driver)
            self.stat_labels['total_laps'].configure(text=str(total_laps))
            self.stat_labels['total_drivers'].configure(text=str(total_drivers))
            self.stat_labels['session_type'].configure(text=session_type)

        except Exception as e:
            print(f"Fehler beim Aktualisieren des Dashboards: {e}")

    # -----------------------------------------------------
    def format_time(self, time_val):
        """Formatiert Zeitwerte benutzerfreundlich"""
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

    # -----------------------------------------------------
    def format_speed(self, speed_val):
        """Formatiert Geschwindigkeitswerte"""
        if pd.isna(speed_val) or speed_val is None:
            return "—"
        try:
            return f"{float(speed_val):.1f}"
        except:
            return "—"

    # -----------------------------------------------------
    def sort_table(self, column):
        """Sortiert die Tabelle nach Spalte"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.fill_laps()

    # -----------------------------------------------------
    def on_filter_changed(self, event=None):
        """Wird aufgerufen wenn Filter-Text geändert wird"""
        self.filter_text = self.filter_entry.get().lower()
        self.fill_laps()

    # -----------------------------------------------------
    def fill_laps(self):
        self.lap_table.delete(*self.lap_table.get_children())
        if self.session is None:
            return

        # Sortiere nach Rundenzeit (schnellste zuerst) für bessere Übersicht
        laps = self.session.laps.copy()

        # Berechne beste Runde für jeden Fahrer
        fastest_laps = {}
        for driver in laps['Driver'].unique():
            driver_laps = laps[laps['Driver'] == driver]
            if not driver_laps.empty:
                fastest = driver_laps.nsmallest(1, 'LapTime')
                if not fastest.empty and pd.notna(fastest.iloc[0]['LapTime']):
                    fastest_laps[driver] = fastest.iloc[0]['LapTime']

        # Sortierung
        if self.sort_column:
            if self.sort_column == "Rundenzeit":
                laps = laps.sort_values(by='LapTime', ascending=self.sort_reverse, na_position='last')
            elif self.sort_column == "Fahrer":
                laps = laps.sort_values(by='Driver', ascending=not self.sort_reverse)
            elif self.sort_column == "Team":
                laps = laps.sort_values(by='Team', ascending=not self.sort_reverse)
            elif self.sort_column == "Runde":
                laps = laps.sort_values(by='LapNumber', ascending=not self.sort_reverse)
            elif self.sort_column == "Pos":
                if 'Position' in laps.columns:
                    laps = laps.sort_values(by='Position', ascending=not self.sort_reverse)
                else:
                    laps = laps.sort_values(by='LapTime', ascending=True, na_position='last')
            else:
                laps = laps.sort_values(by=['LapTime', 'LapNumber'], ascending=[True, True], na_position='last')
        else:
            # Standard: nach Position oder Rundenzeit
            if 'Position' in laps.columns:
                laps = laps.sort_values(by=['Position', 'LapNumber'], ascending=[True, True])
            else:
                laps = laps.sort_values(by=['LapTime', 'LapNumber'], ascending=[True, True], na_position='last')

        laps = laps.reset_index(drop=True)

        # Finde beste Zeit der Session
        valid_laps = laps[laps['LapTime'].notna()]
        if not valid_laps.empty:
            best_lap_time = valid_laps['LapTime'].min()
        else:
            best_lap_time = None

        position_counter = {}
        for idx, lap in laps.iterrows():
            driver = lap.get("Driver", "")
            lap_num_raw = lap.get("LapNumber", "")

            # Filter anwenden
            if self.filter_text:
                if self.filter_text not in driver.lower() and self.filter_text not in str(lap.get("Team", "")).lower():
                    continue

            # Konvertiere LapNumber zu Integer
            try:
                lap_num = int(float(lap_num_raw)) if pd.notna(lap_num_raw) else 0
            except (ValueError, TypeError):
                lap_num = 0

            # Position berechnen
            if 'Position' in lap and pd.notna(lap['Position']):
                pos = int(lap['Position'])
            else:
                if driver not in position_counter:
                    position_counter[driver] = len(position_counter) + 1
                pos = position_counter[driver]

            # Team Name
            team = lap.get("Team", "")
            if pd.isna(team) or team == "":
                team = "—"

            # Rundenzeit
            lap_time = self.format_time(lap.get("LapTime"))

            # Sektoren
            s1 = self.format_time(lap.get("Sector1Time"))
            s2 = self.format_time(lap.get("Sector2Time"))
            s3 = self.format_time(lap.get("Sector3Time"))

            # Durchschnittsgeschwindigkeit
            avg_speed = self.format_speed(lap.get("Speed", ""))

            # Ist das die beste Runde des Fahrers?
            is_best = ""
            if driver in fastest_laps and pd.notna(lap.get("LapTime")):
                if lap['LapTime'] == fastest_laps[driver]:
                    is_best = "⭐"

            # Einzigartige ID für jede Zeile
            iid = f"{driver}_{lap_num}"

            # Markiere beste Runde der Session
            tags = []
            if best_lap_time is not None and pd.notna(lap.get("LapTime")):
                if lap['LapTime'] == best_lap_time:
                    tags = ['best_session']

            self.lap_table.insert(
                "",
                "end",
                iid=iid,
                tags=tags,
                values=(
                    str(pos),
                    driver,
                    team,
                    str(lap_num) if lap_num > 0 else "—",
                    lap_time,
                    s1,
                    s2,
                    s3,
                    avg_speed,
                    is_best,
                ),
            )

        # Tag-Styling für beste Runde
        self.lap_table.tag_configure('best_session', background='#2a4a2a')

        # Update Dashboard
        self.update_dashboard()

    # -----------------------------------------------------
    def fill_drivers(self):
        # Lösche alte Buttons
        for btn in self.driver_buttons:
            btn.destroy()
        self.driver_buttons.clear()

        if self.session is None:
            return

        drivers = sorted(set(self.session.laps["Driver"]))
        for d in drivers:
            btn = ctk.CTkButton(self.driver_scroll, text=d,
                              command=lambda driver=d: self.on_driver_selected(driver),
                              width=100, height=30,
                              fg_color=("gray70", "gray30"))
            btn.pack(pady=2, padx=5, fill="x")
            self.driver_buttons.append(btn)

        # Update Vergleichs-Comboboxes
        self.compare_driver1.configure(values=drivers)
        self.compare_driver2.configure(values=drivers)

    # -----------------------------------------------------
    def on_driver_selected(self, driver):
        if self.session is None:
            return

        laps = self.session.laps.pick_drivers(driver)
        if laps.empty:
            return

        lap = laps.pick_fastest()
        self.current_lap = lap
        self.plot_lap(lap)

    # -----------------------------------------------------
    def on_lap_selected(self, event):
        if self.session is None:
            return
        sel = self.lap_table.selection()
        if not sel:
            return

        iid = sel[0]
        driver, lapnum = iid.rsplit("_", 1)
        try:
            lapnum = int(float(lapnum))
        except (ValueError, TypeError):
            messagebox.showerror("Fehler", f"Ungültige Rundennummer: {lapnum}")
            return

        lap = self.session.laps[(self.session.laps["Driver"] == driver) & (self.session.laps["LapNumber"] == lapnum)]
        if lap.empty:
            return
        lap = lap.iloc[0]
        self.plot_lap(lap)

    # -----------------------------------------------------
    def plot_lap(self, lap):
        try:
            tel = lap.get_car_data().add_distance()
            if tel is None or tel.empty:
                messagebox.showerror("Keine Telemetrie", "Keine Telemetriedaten für diese Runde verfügbar.")
                return

            dist = tel["Distance"]
            driver_name = lap.get('Driver', 'Unbekannt')
            lap_num = lap.get('LapNumber', '?')

            text_color = self.plot_text_color
            bg_color = self.plot_bg_color
            border_color = self.plot_border_color

            # === TAB 1: Geschwindigkeit ===
            self.ax.clear()
            self.ax.set_facecolor(bg_color)

            speed = tel["Speed"]
            self.ax.plot(dist, speed, color=self.accent_color, linewidth=2.5, alpha=0.9)
            self.ax.fill_between(dist, speed, alpha=0.3, color=self.accent_color)

            self.ax.set_xlabel("Streckendistanz (m)", color=text_color, fontsize=10)
            self.ax.set_ylabel("Geschwindigkeit (km/h)", color=text_color, fontsize=10)
            self.ax.set_title(f"🏎️ {driver_name} – Runde {lap_num}",
                            color=text_color, fontsize=12, fontweight='bold', pad=15)
            self.ax.grid(True, alpha=0.2, color=border_color, linestyle='--', linewidth=0.5)
            for spine in self.ax.spines.values():
                spine.set_color(border_color)
            self.ax.tick_params(colors=text_color, labelsize=9)

            # === TAB 2: Gas & Bremse ===
            self.ax2.clear()
            self.ax2.set_facecolor(bg_color)

            if 'Throttle' in tel.columns and 'Brake' in tel.columns:
                throttle = tel["Throttle"] * 100
                brake = tel["Brake"] * 100

                self.ax2.plot(dist, throttle, color='#00d4aa', linewidth=2, label='Gas', alpha=0.8)
                self.ax2.plot(dist, brake, color='#ff4444', linewidth=2, label='Bremse', alpha=0.8)
                self.ax2.fill_between(dist, throttle, alpha=0.2, color='#00d4aa')
                self.ax2.fill_between(dist, brake, alpha=0.2, color='#ff4444')
                self.ax2.legend(loc='upper right', facecolor=bg_color,
                              edgecolor=border_color, labelcolor=text_color)
            else:
                self.ax2.text(0.5, 0.5, 'Gas- und Bremse-Daten\nnicht verfügbar',
                            transform=self.ax2.transAxes, ha='center', va='center',
                            fontsize=11, color=text_color)

            self.ax2.set_xlabel("Streckendistanz (m)", color=text_color, fontsize=10)
            self.ax2.set_ylabel("Prozent (%)", color=text_color, fontsize=10)
            self.ax2.set_title(f"⚡ {driver_name} – Gas & Bremse",
                             color=text_color, fontsize=12, fontweight='bold', pad=15)
            self.ax2.grid(True, alpha=0.2, color=border_color, linestyle='--', linewidth=0.5)
            for spine in self.ax2.spines.values():
                spine.set_color(border_color)
            self.ax2.tick_params(colors=text_color, labelsize=9)
            self.ax2.set_ylim(0, 105)

            # === TAB 3: RPM & Gänge ===
            self.ax3.clear()
            self.ax3.set_facecolor(bg_color)

            if 'RPM' in tel.columns:
                rpm = tel["RPM"]
                ax3_twin = self.ax3.twinx()

                self.ax3.plot(dist, rpm, color='#ffaa00', linewidth=2.5, alpha=0.9, label='RPM')
                self.ax3.fill_between(dist, rpm, alpha=0.3, color='#ffaa00')

                if 'nGear' in tel.columns:
                    gear = tel["nGear"]
                    ax3_twin.plot(dist, gear, color='#00aaff', linewidth=2, alpha=0.8, label='Gang', linestyle='--')
                    ax3_twin.set_ylabel("Gang", color='#00aaff', fontsize=10)
                    ax3_twin.tick_params(colors='#00aaff', labelsize=9)
                    ax3_twin.set_ylim(0.5, 8.5)

                self.ax3.set_ylabel("RPM (U/min)", color='#ffaa00', fontsize=10)
                self.ax3.tick_params(colors='#ffaa00', labelsize=9)
            else:
                self.ax3.text(0.5, 0.5, 'RPM-Daten\nnicht verfügbar',
                            transform=self.ax3.transAxes, ha='center', va='center',
                            fontsize=11, color=text_color)

            self.ax3.set_xlabel("Streckendistanz (m)", color=text_color, fontsize=10)
            self.ax3.set_title(f"🔧 {driver_name} – Motor & Getriebe",
                             color=text_color, fontsize=12, fontweight='bold', pad=15)
            self.ax3.grid(True, alpha=0.2, color=border_color, linestyle='--', linewidth=0.5)
            for spine in self.ax3.spines.values():
                spine.set_color(border_color)

            # === TAB 4: Vergleich (wird separat gefüllt) ===
            self.ax4.clear()
            self.ax4.set_facecolor(bg_color)
            self.ax4.text(0.5, 0.5, 'Wähle zwei Fahrer aus,\num sie zu vergleichen',
                        transform=self.ax4.transAxes, ha='center', va='center',
                        fontsize=12, color=text_color, style='italic')
            self.ax4.set_xticks([])
            self.ax4.set_yticks([])

            # Update alle Canvas
            for fig in [self.fig, self.fig2, self.fig3, self.fig4]:
                fig.patch.set_facecolor(bg_color)

            self.canvas.draw()
            self.canvas2.draw()
            self.canvas3.draw()
            self.canvas4.draw()

        except Exception as e:
            messagebox.showerror("Plot Fehler", f"Fehler beim Erstellen der Grafiken:\n{str(e)}")

    # -----------------------------------------------------
    def compare_drivers(self):
        """Vergleicht zwei Fahrer direkt"""
        if self.session is None:
            messagebox.showerror("Fehler", "Keine Session geladen.")
            return

        driver1 = self.compare_driver1.get()
        driver2 = self.compare_driver2.get()

        if not driver1 or not driver2:
            messagebox.showerror("Fehler", "Bitte wählen Sie beide Fahrer aus.")
            return

        if driver1 == driver2:
            messagebox.showerror("Fehler", "Bitte wählen Sie zwei verschiedene Fahrer aus.")
            return

        try:
            # Beste Runden beider Fahrer
            laps1 = self.session.laps.pick_drivers(driver1)
            laps2 = self.session.laps.pick_drivers(driver2)

            if laps1.empty or laps2.empty:
                messagebox.showerror("Fehler", "Nicht genügend Daten für den Vergleich verfügbar.")
                return

            lap1 = laps1.pick_fastest()
            lap2 = laps2.pick_fastest()

            tel1 = lap1.get_car_data().add_distance()
            tel2 = lap2.get_car_data().add_distance()

            if tel1 is None or tel1.empty or tel2 is None or tel2.empty:
                messagebox.showerror("Fehler", "Telemetriedaten für den Vergleich nicht verfügbar.")
                return

            dist1 = tel1["Distance"]
            dist2 = tel2["Distance"]
            speed1 = tel1["Speed"]
            speed2 = tel2["Speed"]

            # Normalisiere Distanz für besseren Vergleich
            try:
                from scipy import interpolate
                import numpy as np

                max_dist = min(dist1.max(), dist2.max())
                common_dist = np.linspace(0, max_dist, 500)

                if len(dist1) > 1 and len(dist2) > 1:
                    f1 = interpolate.interp1d(dist1, speed1, bounds_error=False, fill_value='extrapolate')
                    f2 = interpolate.interp1d(dist2, speed2, bounds_error=False, fill_value='extrapolate')
                    speed1_interp = f1(common_dist)
                    speed2_interp = f2(common_dist)
                else:
                    common_dist = dist1
                    speed1_interp = speed1
                    speed2_interp = speed2
            except ImportError:
                common_dist = dist1
                speed1_interp = speed1
                if len(dist2) > 0:
                    speed2_interp = speed2
                else:
                    speed2_interp = speed1

            # Plot Vergleich
            text_color = self.plot_text_color
            bg_color = self.plot_bg_color
            border_color = self.plot_border_color

            self.ax4.clear()
            self.ax4.set_facecolor(bg_color)

            self.ax4.plot(common_dist, speed1_interp, color='#e10600', linewidth=2.5,
                         label=f"{driver1} ({self.format_time(lap1['LapTime'])})", alpha=0.9)
            self.ax4.plot(common_dist, speed2_interp, color='#00aaff', linewidth=2.5,
                         label=f"{driver2} ({self.format_time(lap2['LapTime'])})", alpha=0.9)

            self.ax4.fill_between(common_dist, speed1_interp, alpha=0.2, color='#e10600')
            self.ax4.fill_between(common_dist, speed2_interp, alpha=0.2, color='#00aaff')

            self.ax4.set_xlabel("Streckendistanz (m)", color=text_color, fontsize=10)
            self.ax4.set_ylabel("Geschwindigkeit (km/h)", color=text_color, fontsize=10)
            self.ax4.set_title(f"⚖️ Vergleich: {driver1} vs {driver2}",
                            color=text_color, fontsize=12, fontweight='bold', pad=15)
            self.ax4.legend(loc='upper right', facecolor=bg_color,
                          edgecolor=border_color, labelcolor=text_color)
            self.ax4.grid(True, alpha=0.2, color=border_color, linestyle='--', linewidth=0.5)
            for spine in self.ax4.spines.values():
                spine.set_color(border_color)
            self.ax4.tick_params(colors=text_color, labelsize=9)

            self.fig4.patch.set_facecolor(bg_color)
            self.canvas4.draw()

        except ImportError:
            messagebox.showerror("Fehler", "Für den Vergleich wird scipy benötigt.\nInstallieren Sie es mit: pip install scipy")
        except Exception as e:
            messagebox.showerror("Vergleich Fehler", f"Fehler beim Vergleich:\n{str(e)}")

    # -----------------------------------------------------
    def export_data(self):
        """Exportiert Tabellendaten als CSV oder Excel"""
        if self.session is None:
            messagebox.showerror("Fehler", "Keine Session geladen.")
            return

        # Erstelle DataFrame aus Tabelle
        data = []
        for item in self.lap_table.get_children():
            values = self.lap_table.item(item, 'values')
            data.append({
                'Position': values[0],
                'Fahrer': values[1],
                'Team': values[2],
                'Runde': values[3],
                'Rundenzeit': values[4],
                'Sektor 1': values[5],
                'Sektor 2': values[6],
                'Sektor 3': values[7],
                'Ø Geschwindigkeit': values[8],
                'Beste': values[9]
            })

        if not data:
            messagebox.showerror("Fehler", "Keine Daten zum Exportieren verfügbar.")
            return

        df = pd.DataFrame(data)

        # Datei-Dialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            if filename.endswith('.xlsx'):
                try:
                    df.to_excel(filename, index=False)
                    messagebox.showinfo("Erfolg", f"Daten wurden nach {filename} exportiert.")
                except ImportError:
                    messagebox.showerror("Fehler", "Für Excel-Export wird openpyxl benötigt.\nInstallieren Sie es mit: pip install openpyxl")
            else:
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Erfolg", f"Daten wurden nach {filename} exportiert.")
        except Exception as e:
            messagebox.showerror("Export Fehler", f"Fehler beim Exportieren:\n{str(e)}")

    # -----------------------------------------------------
    def export_plot(self):
        """Exportiert die aktuelle Grafik als PNG"""
        # Finde aktiven Tab
        # Da wir keinen direkten Zugriff auf den aktiven Tab haben, exportieren wir alle Plots
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            # Exportiere alle Plots
            if filename.endswith('.pdf'):
                from matplotlib.backends.backend_pdf import PdfPages
                with PdfPages(filename) as pdf:
                    for fig in [self.fig, self.fig2, self.fig3, self.fig4]:
                        pdf.savefig(fig, bbox_inches='tight')
                messagebox.showinfo("Erfolg", f"Alle Grafiken wurden nach {filename} exportiert.")
            else:
                # Exportiere nur die erste Grafik (Geschwindigkeit)
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.fig.get_facecolor())
                messagebox.showinfo("Erfolg", f"Grafik wurde nach {filename} exportiert.")
        except Exception as e:
            messagebox.showerror("Export Fehler", f"Fehler beim Exportieren:\n{str(e)}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = F1TkApp(root)
    root.mainloop()
