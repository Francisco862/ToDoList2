import tkinter as tk
from tkinter import ttk

# Kolory dopasowane do list_view/week_view
BG_PANEL = "#0f1724"
CARD_BG = "#111827"
BTN_BG = "#0b1220"
BTN_HOVER = "#17203a"
TEXT_COLOR = "#F3F4F6"
ROUND_RADIUS = 20

# ⭐ BRAKOWAŁO TEGO – dodane!
MUTED = "#9CA3AF"

class RoundedFrame(tk.Frame):
    def __init__(self, master, radius=20, inner_bg=CARD_BG, **kwargs):
        super().__init__(master, bg=master.cget("bg"), **kwargs)

        self.radius = radius
        self.inner_bg = inner_bg

        self.canvas = tk.Canvas(self, bg=master.cget("bg"), highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=self.inner_bg, bd=0, highlightthickness=0)

        self._win_id = self.canvas.create_window(
            0, 0, anchor="nw", window=self.inner
        )

        self.canvas.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.canvas.delete("round")

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 2 or h < 2:
            return

        r = min(self.radius, w // 2, h // 2)

        points = [
            r, 0,
            w - r, 0,
            w, r,
            w, h - r,
            w - r, h,
            r, h,
            0, h - r,
            0, r,
        ]

        self.canvas.create_polygon(
            points,
            smooth=True,
            fill=self.inner_bg,
            outline="",
            tags="round",
        )

        self.canvas.coords(self._win_id, 0, 0)
        self.canvas.itemconfig(self._win_id, width=w, height=h)



class Sidebar(tk.Frame):
    def __init__(self, root, app, **kwargs):
        super().__init__(root, bg=BG_PANEL, width=220, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        card = RoundedFrame(self, inner_bg=CARD_BG)
        card.pack(fill="both", expand=True, padx=8, pady=12)
        inner = card.inner

        title = tk.Label(inner, text="📌 To-Do PRO", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 16, "bold"))
        title.pack(pady=(14,12), padx=12, anchor="w")

        btns = [
            ("📄 Lista zadań", "list"),
            ("📅 Widok tygodnia", "week"),
            ("🗓️ Kalendarz", "calendar"),
        ]
        for txt, view in btns:
            b = tk.Label(inner, text=txt, bg=BTN_BG, fg=TEXT_COLOR, font=("Segoe UI", 12), relief="flat", padx=12, pady=10)
            b.pack(fill="x", padx=12, pady=6)
            b.bind("<Button-1>", lambda e, v=view: self.app.show(v))
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BTN_HOVER))
            b.bind("<Leave>", lambda e, w=b: w.config(bg=BTN_BG))

        tk.Frame(inner, height=1, bg="#0b1226").pack(fill="x", padx=12, pady=10)

        theme_btn = tk.Label(inner, text="🌙 / ☀️ Tryb", bg=BTN_BG, fg=TEXT_COLOR, font=("Segoe UI", 12), padx=12, pady=8)
        theme_btn.pack(fill="x", padx=12, pady=(8,6))
        theme_btn.bind("<Button-1>", lambda e: self._toggle_theme())
        theme_btn.bind("<Enter>", lambda e, w=theme_btn: w.config(bg=BTN_HOVER))
        theme_btn.bind("<Leave>", lambda e, w=theme_btn: w.config(bg=BTN_BG))

        # ⭐ tutaj był błąd → brak MUTED
        self.current_label = tk.Label(inner, text="Widok: —", bg=CARD_BG, fg=MUTED, font=("Segoe UI", 9))
        self.current_label.pack(side="bottom", anchor="w", padx=12, pady=8)

    def set_current(self, name: str):
        self.current_label.config(text=f"Widok: {name}")

    def _toggle_theme(self):
        try:
            if hasattr(self.app, "theme") and hasattr(self.app.theme, "toggle"):
                self.app.theme.toggle()
                if hasattr(self.app, "refresh_all_views"):
                    self.app.refresh_all_views()
        except Exception:
            pass
