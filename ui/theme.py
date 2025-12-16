import tkinter as tk
from tkinter import ttk

class Theme:
    def __init__(self, root):
        self.dark = False
        self.root = root

        self.light_bg = "#f4f4f4"
        self.light_fg = "#000"
        self.dark_bg = "#1e1e1e"
        self.dark_fg = "#fff"

        self.priority_colors_light = {
            "Low": "#d1ffd1",
            "Normal": "#fff7c2",
            "High": "#ffc2c2",
            "Urgent": "#ff6b6b"
        }

        self.priority_colors_dark = {
            "Low": "#2a4d2a",
            "Normal": "#4d4422",
            "High": "#4d2222",
            "Urgent": "#a30000"
        }

        self.apply()

    @property
    def bg(self):
        return self.dark_bg if self.dark else self.light_bg

    @property
    def fg(self):
        return self.dark_fg if self.dark else self.light_fg

    @property
    def priority_colors(self):
        return self.priority_colors_dark if self.dark else self.priority_colors_light

    def toggle(self):
        self.dark = not self.dark
        self.apply()

    def apply(self):
        self.root.config(bg=self.bg)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.fg)
        style.configure("TButton", padding=6, background="#444" if self.dark else "#eee",
                        foreground=self.fg, focusthickness=3, borderwidth=1)
        style.map("TButton",
            background=[("active", "#666" if self.dark else "#ddd")]
        )

        style.configure("Treeview", background=self.bg, fieldbackground=self.bg,
                        foreground=self.fg, rowheight=28)
        style.map("Treeview",
            background=[("selected", "#555" if self.dark else "#ccc")]
        )
