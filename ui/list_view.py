# ui/list_view.py
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import DateEntry

from core.manager import TaskManager
from core.models import Task

# ---- Kolory i stałe (macOS Big Sur - dark rounded) ----
BG_PANEL = "#0f1724"       # tło kontenera
CARD_BG = "#111827"        # tło kart/paneli
CELL_BG = "#0b1220"        # tło komórek / pola wejścia
TEXT_COLOR = "#F3F4F6"     # jasny tekst
MUTED = "#9CA3AF"

NOTES_FILE = os.path.join(os.path.dirname(__file__), "..", "notes.txt")

# Zaokrąglenia - styl B (macOS Big Sur)
ROUND_RADIUS = 24


class RoundedFrame(tk.Frame):
    """
    Prostokąt o zaokrąglonych rogach z wewnętrznym Frame do umieszczania widgetów.
    (Tk nie ma prawdziwych rounded-corner widgets — rysujemy na canvasie).
    Używaj .inner jako kontenera do pack/grid.
    """
    def __init__(self, master, radius=ROUND_RADIUS, bg=CARD_BG, inner_bg=None, **kwargs):
        super().__init__(master, bg=bg, **kwargs)
        self.radius = radius
        self.bg = bg
        self.inner_bg = inner_bg or bg

        self.canvas = tk.Canvas(self, bg=self.bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=self.inner_bg)
        self._window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.canvas.delete("rounded")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        r = min(self.radius, w // 2, h // 2)
        if w <= 1 or h <= 1:
            return
        # łatwe przybliżenie zaokrąglonego prostokąta przez polygon (smooth=True)
        pts = [
            r, 0,
            w - r, 0,
            w, r,
            w, h - r,
            w - r, h,
            r, h,
            0, h - r,
            0, r
        ]
        self.canvas.create_polygon(pts, smooth=True, fill=self.inner_bg, outline="", tags=("rounded",))
        # upewnij się, że inner frame ma rozmiar
        self.canvas.coords(self._window, 0, 0)
        self.canvas.itemconfig(self._window, width=w, height=h)


class ListView(tk.Frame):
    PRIORITY_COLORS = {
        "Wysoki": "#EF4444",   # czerwony
        "Średni": "#F59E0B",   # żółto-pomarańczowy
        "Niski":  "#10B981",   # zielony
        "Normal": "#6B7280",   # neutralny
    }

    PRIORITY_ICONS = {
        "Wysoki": "⚠️",
        "Średni": "⭐",
        "Niski": "✅",
        "Normal": "•",
    }

    def __init__(self, master, manager: TaskManager, **kwargs):
        super().__init__(master, bg=BG_PANEL, **kwargs)
        self.manager = manager

        # zmienne
        self.search_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="Wszystkie")
        self.sort_var = tk.StringVar(value="Termin rosnąco")

        # statystyki
        self.sum_total = tk.StringVar()
        self.sum_done = tk.StringVar()
        self.sum_not_done = tk.StringVar()

        # inicjalizacja UI
        self._setup_styles()
        self._build_ui()
        self.refresh()

    # ---- show/hide (używane przez TodoApp.show) ----
    def show(self):
        # pakujemy zawartość tak, żeby była w widoku 'content_frame' używanym w app.py
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()

    # ---- style dla treeview ----
    def _setup_styles(self):
        style = ttk.Style()
        # użyj domyślnego motywu i nadpisz
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("List.Treeview",
                        background=CELL_BG,
                        fieldbackground=CELL_BG,
                        foreground=TEXT_COLOR,
                        rowheight=28,
                        font=("Segoe UI", 11))
        style.configure("List.Treeview.Heading",
                        background=CARD_BG,
                        foreground=TEXT_COLOR,
                        font=("Segoe UI", 12, "bold"))
        style.map("List.Treeview", background=[("selected", "#1f2937")], foreground=[("selected", "#fff")])

    # ---- budowa UI ----
    def _build_ui(self):
        # HEADER (karta z zaokrągleniem)
        header_card = RoundedFrame(self, radius=ROUND_RADIUS, inner_bg=CARD_BG)
        header_card.pack(fill="x", padx=20, pady=(18, 8))
        header = tk.Frame(header_card.inner, bg=CARD_BG)
        header.pack(fill="x", padx=14, pady=10)

        tk.Label(header, text="📝", font=("Segoe UI Emoji", 20), bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
        tk.Label(header, text="Lista zadań", font=("Segoe UI", 20, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(side="left", padx=(8, 0))

        # toolbar card
        toolbar_card = RoundedFrame(self, radius=ROUND_RADIUS, inner_bg=CARD_BG)
        toolbar_card.pack(fill="x", padx=20, pady=(6, 12))
        toolbar = tk.Frame(toolbar_card.inner, bg=CARD_BG)
        toolbar.pack(fill="x", padx=12, pady=10)

        # Szukaj
        sframe = tk.Frame(toolbar, bg=CARD_BG)
        sframe.pack(side="left")
        tk.Label(sframe, text="Szukaj:", bg=CARD_BG, fg=MUTED).pack(side="left", padx=(0, 6))
        search_entry = tk.Entry(sframe, textvariable=self.search_var, bg=CELL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat", width=30)
        search_entry.pack(side="left")
        self.search_var.trace("w", lambda *_: self.refresh())

        # Status filter
        fframe = tk.Frame(toolbar, bg=CARD_BG)
        fframe.pack(side="left", padx=14)
        tk.Label(fframe, text="Status:", bg=CARD_BG, fg=MUTED).pack(side="left", padx=(0, 6))
        self.status_cb = ttk.Combobox(fframe, textvariable=self.status_filter_var, values=["Wszystkie", "Otwarte", "Zrobione"], state="readonly", width=12)
        self.status_cb.pack(side="left")
        self.status_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Sortowanie
        sframe2 = tk.Frame(toolbar, bg=CARD_BG)
        sframe2.pack(side="left", padx=14)
        tk.Label(sframe2, text="Sortuj:", bg=CARD_BG, fg=MUTED).pack(side="left", padx=(0, 6))
        self.sort_cb = ttk.Combobox(sframe2, textvariable=self.sort_var, values=["Termin rosnąco", "Termin malejąco", "Priorytet (wysoki->niski)", "Projekt A→Z"], state="readonly", width=22)
        self.sort_cb.pack(side="left")
        self.sort_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # tabela (karta)
        table_card = RoundedFrame(self, radius=ROUND_RADIUS, inner_bg=CARD_BG)
        table_card.pack(fill="both", expand=False, padx=20, pady=(0, 12))
        table_wrap = tk.Frame(table_card.inner, bg=CARD_BG)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=10)

        columns = ("Tytuł", "Priorytet", "Termin", "Projekt", "Status")
        vsb = ttk.Scrollbar(table_wrap, orient="vertical")
        vsb.pack(side="right", fill="y")
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", style="List.Treeview", yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.config(command=self.tree.yview)
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("Tytuł", width=420, anchor="w")
        self.tree.column("Priorytet", width=110, anchor="center")
        self.tree.column("Termin", width=170, anchor="center")
        self.tree.column("Projekt", width=140, anchor="center")
        self.tree.column("Status", width=90, anchor="center")

        # quick-add card (karta dolna)
        add_card = RoundedFrame(self, radius=ROUND_RADIUS, inner_bg=CARD_BG)
        add_card.pack(fill="x", padx=20, pady=(0, 12))
        form = tk.Frame(add_card.inner, bg=CARD_BG)
        form.pack(fill="x", padx=12, pady=10)

        # tytuł
        self.title_entry = tk.Entry(form, bg=CELL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, relief="flat", width=36)
        self.title_entry.grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")

        # priorytet/projekt
        self.priority_cb = ttk.Combobox(form, values=list(self.PRIORITY_COLORS.keys()), state="readonly", width=10)
        self.priority_cb.set("Średni")
        self.priority_cb.grid(row=0, column=1, padx=4)
        self.project_cb = ttk.Combobox(form, values=["General", "Praca", "Szkoła", "Dom"], state="readonly", width=14)
        self.project_cb.set("General")
        self.project_cb.grid(row=0, column=2, padx=4)

        # data + godzina
        tk.Label(form, text="Data:", bg=CARD_BG, fg=MUTED).grid(row=0, column=3, padx=(10, 2))
        self.date_entry = DateEntry(form, width=12, locale="pl_PL", date_pattern="dd.MM.yyyy", background="#0b1220", foreground="white", borderwidth=0)
        self.date_entry.grid(row=0, column=4, padx=(0, 6))
        tk.Label(form, text="Godz.:", bg=CARD_BG, fg=MUTED).grid(row=0, column=5)
        self.hour_var = tk.StringVar(value="12")
        self.minute_var = tk.StringVar(value="00")
        tk.Spinbox(form, from_=0, to=23, width=3, textvariable=self.hour_var, format="%02.0f", bg=CELL_BG, fg=TEXT_COLOR, relief="flat").grid(row=0, column=6, padx=(4,2))
        tk.Label(form, text=":", bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=7)
        tk.Spinbox(form, from_=0, to=59, width=3, textvariable=self.minute_var, format="%02.0f", bg=CELL_BG, fg=TEXT_COLOR, relief="flat").grid(row=0, column=8, padx=(2,10))

        # akcje
        btns = tk.Frame(form, bg=CARD_BG)
        btns.grid(row=0, column=9, padx=(0,0))
        def make_btn(text, cmd, bgc):
            return tk.Button(btns, text=text, command=cmd, bg=bgc, fg="white", relief="flat", padx=10, pady=6)
        make_btn("➕ Dodaj", self.add, "#2563EB").grid(row=0, column=0, padx=4)
        make_btn("✏️ Edytuj", self.edit, "#7C3AED").grid(row=0, column=1, padx=4)
        make_btn("✔ Zrobione", self.done, "#16A34A").grid(row=0, column=2, padx=4)
        make_btn("🗑 Usuń", self.delete, "#DC2626").grid(row=0, column=3, padx=4)

        # bottom big card: stats + widgets + notes
        bottom_card = RoundedFrame(self, radius=ROUND_RADIUS, inner_bg=CARD_BG)
        bottom_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        bottom = tk.Frame(bottom_card.inner, bg=CARD_BG)
        bottom.pack(fill="both", expand=True, padx=12, pady=10)

        # stats
        stats = tk.Frame(bottom, bg=CARD_BG)
        stats.pack(fill="x")
        def stat_box(parent, title, var):
            box = RoundedFrame(parent, radius=16, inner_bg="#0b1226")
            box.pack(side="left", padx=8, pady=4, ipadx=10, ipady=6, expand=True, fill="x")
            tk.Label(box.inner, text=title, bg="#0b1226", fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(box.inner, textvariable=var, bg="#0b1226", fg=TEXT_COLOR, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        stat_box(stats, "Wszystkie", self.sum_total)
        stat_box(stats, "Zrobione", self.sum_done)
        stat_box(stats, "Do zrobienia", self.sum_not_done)

        # widgets row
        widgets_row = tk.Frame(bottom, bg=CARD_BG)
        widgets_row.pack(fill="x", pady=(12,6))
        self.widget_priority = RoundedFrame(widgets_row, radius=16, inner_bg=CARD_BG)
        self.widget_priority.pack(side="left", expand=True, fill="both", padx=6)
        tk.Label(self.widget_priority.inner, text="🔥 Wysoki priorytet", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4,6))
        self.widget_deadlines = RoundedFrame(widgets_row, radius=16, inner_bg=CARD_BG)
        self.widget_deadlines.pack(side="left", expand=True, fill="both", padx=6)
        tk.Label(self.widget_deadlines.inner, text="⏳ Najbliższe terminy", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4,6))

        # notes area (expanding)
        notes_wrap = tk.Frame(bottom, bg=CARD_BG)
        notes_wrap.pack(fill="both", expand=True, pady=(8,0))
        notes_label = tk.Label(notes_wrap, text="📝 Notatki", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
        notes_label.pack(anchor="w")
        notes_card = RoundedFrame(notes_wrap, radius=16, inner_bg="#071021")
        notes_card.pack(fill="both", expand=True, pady=(6,0))
        # scrollbar
        notes_scroll = ttk.Scrollbar(notes_card.inner)
        notes_scroll.pack(side="right", fill="y")
        self.notes_text = tk.Text(notes_card.inner, bg="#071021", fg=TEXT_COLOR, insertbackground=TEXT_COLOR, wrap="word", relief="flat")
        self.notes_text.pack(fill="both", expand=True, padx=6, pady=6)
        notes_scroll.config(command=self.notes_text.yview)
        self.notes_text.config(yscrollcommand=notes_scroll.set)

        # automatyczne ładowanie i zapis notatek
        self._load_notes()
        self.notes_text.bind("<KeyRelease>", lambda e: self._save_notes())

        # double-click open edit
        self.tree.bind("<Double-1>", lambda e: self.edit())

    # ---- notatki ----
    def _load_notes(self):
        try:
            if os.path.exists(NOTES_FILE):
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    self.notes_text.delete("1.0", "end")
                    self.notes_text.insert("1.0", f.read())
        except Exception:
            pass

    def _save_notes(self):
        try:
            s = self.notes_text.get("1.0", "end").rstrip()
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                f.write(s)
        except Exception:
            pass

    # ---- summary & widgets ----
    def _update_summary(self):
        tasks = self.manager.tasks
        done = [t for t in tasks if t.status == "Done"]
        not_done = [t for t in tasks if t.status != "Done"]
        self.sum_total.set(str(len(tasks)))
        self.sum_done.set(str(len(done)))
        self.sum_not_done.set(str(len(not_done)))

    def _update_widgets(self):
        # clear
        for w in self.widget_priority.inner.winfo_children():
            if isinstance(w, tk.Label) and w.cget("text").startswith(("🔥", "⚠")):
                w.destroy()
        for w in self.widget_deadlines.inner.winfo_children():
            if isinstance(w, tk.Label) and (w.cget("text").startswith("⏳") or "—" in w.cget("text")):
                w.destroy()

        now = datetime.now()
        urgent = [t for t in self.manager.tasks if t.priority == "Wysoki" and (t.due is None or t.due >= now)]
        urgent = sorted(urgent, key=lambda t: t.due or datetime.max)[:6]
        deadlines = sorted([t for t in self.manager.tasks if t.due], key=lambda t: t.due)[:6]

        for t in urgent:
            time_str = t.due.strftime("%H:%M") if t.due else "--:--"
            tk.Label(self.widget_priority.inner, text=f"⚠️ {t.title} — {time_str}", bg=self.widget_priority.inner.cget("bg"), fg="#FCA5A5", anchor="w").pack(fill="x", pady=2)
        for t in deadlines:
            time_str = t.due.strftime("%d.%m.%Y %H:%M")
            tk.Label(self.widget_deadlines.inner, text=f"⏳ {t.title} — {time_str}", bg=self.widget_deadlines.inner.cget("bg"), fg="#93C5FD", anchor="w").pack(fill="x", pady=2)

    # ---- refresh (filtry + sortowanie) ----
    def refresh(self):
        q = (self.search_var.get() or "").lower().strip()
        status_f = self.status_filter_var.get()
        sort_mode = self.sort_var.get()

        items = []
        for t in self.manager.tasks:
            if q and q not in (t.title or "").lower():
                continue
            if status_f == "Otwarte" and t.status == "Done":
                continue
            if status_f == "Zrobione" and t.status != "Done":
                continue
            items.append(t)

        # sort
        if sort_mode == "Termin rosnąco":
            items.sort(key=lambda x: x.due or datetime.max)
        elif sort_mode == "Termin malejąco":
            items.sort(key=lambda x: x.due or datetime.min, reverse=True)
        elif sort_mode == "Priorytet (wysoki->niski)":
            order = {"Wysoki": 0, "Średni": 1, "Niski": 2, "Normal": 3}
            items.sort(key=lambda x: order.get(x.priority, 99))
        elif sort_mode == "Projekt A→Z":
            items.sort(key=lambda x: (x.project or "").lower())

        # wyczyść
        for r in self.tree.get_children():
            self.tree.delete(r)

        for t in items:
            due_str = t.due.strftime("%d.%m.%Y %H:%M") if t.due else "-"
            status_mark = "✔" if t.status == "Done" else "-"
            # dodaj badge priorytetu w kolumnie Priorytet - ikonka + tekst
            pri = f"{self.PRIORITY_ICONS.get(t.priority, '')} {t.priority}"
            self.tree.insert(
                "",
                "end",
                iid=str(t.id),
                values=(t.title, t.priority, due_str, t.project, status_mark),
                tags=(t.priority,),
            )

        # kolorowanie wierszy wg priorytetu
        for k, v in self.PRIORITY_COLORS.items():
            self.tree.tag_configure(k, background=v, foreground="#071021")

        self._update_summary()
        self._update_widgets()

    # ---- selection helper ----
    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        for t in self.manager.tasks:
            if t.id == iid:
                return t
        return None

    # ---- CRUD operations ----
    def add(self):
        title = (self.title_entry.get() or "").strip()
        if not title:
            return
        # data + godzina
        d = self.date_entry.get_date()
        try:
            h = int(self.hour_var.get()); m = int(self.minute_var.get())
        except ValueError:
            h = 12; m = 0
        due = datetime(year=d.year, month=d.month, day=d.day, hour=h, minute=m)
        task = Task(title=title, priority=self.priority_cb.get() or "Normal", project=self.project_cb.get() or "General", due=due)
        self.manager.add(task)
        self.title_entry.delete(0, "end")
        self.refresh()

    def delete(self):
        t = self.get_selected()
        if not t: return
        self.manager.delete(t.id)
        self.refresh()

    def done(self):
        t = self.get_selected()
        if not t: return
        t.status = "Done"
        self.manager.update(t)
        self.refresh()

    # ---- edit modal (centered, modal) ----
    def edit(self):
        t = self.get_selected()
        if not t:
            return
        self._open_edit_dialog(t)

    def _open_edit_dialog(self, task: Task):
        root = self.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.transient(root)
        dlg.grab_set()
        dlg.title("Edytuj zadanie")
        dlg.configure(bg=CARD_BG)
        # center on parent
        root.update_idletasks()
        rx = root.winfo_rootx(); ry = root.winfo_rooty(); rw = root.winfo_width(); rh = root.winfo_height()
        w, h = 520, 520
        x = rx + max(10, (rw - w)//2); y = ry + max(10, (rh - h)//2)
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        cont = tk.Frame(dlg, bg=CARD_BG, padx=14, pady=12)
        cont.pack(fill="both", expand=True)

        tk.Label(cont, text="Edytuj zadanie", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(cont, text=f"Aktualny status: {task.status}", bg=CARD_BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(0,6))

        tk.Label(cont, text="Tytuł:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
        title_e = tk.Entry(cont, bg=CELL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        title_e.insert(0, task.title or "")
        title_e.pack(fill="x")

        tk.Label(cont, text="Projekt:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
        project_e = tk.Entry(cont, bg=CELL_BG, fg=TEXT_COLOR)
        project_e.insert(0, task.project or "")
        project_e.pack(fill="x")

        tk.Label(cont, text="Priorytet:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
        pr_cb = ttk.Combobox(cont, values=list(self.PRIORITY_COLORS.keys()), state="readonly")
        pr_cb.set(task.priority or "Normal")
        pr_cb.pack(fill="x")

        tk.Label(cont, text="Opis:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
        desc = tk.Text(cont, height=6, bg=CELL_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        desc.insert("1.0", task.description or "")
        desc.pack(fill="both", expand=True)

        tk.Label(cont, text="Termin:", bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(8,2))
        due_base = task.due or datetime.now()
        d_frame = tk.Frame(cont, bg=CARD_BG)
        d_frame.pack(anchor="w")
        date_e = DateEntry(d_frame, locale="pl_PL", date_pattern="dd.MM.yyyy")
        date_e.set_date(due_base.date())
        date_e.pack(side="left", padx=(0,10))
        hour_v = tk.StringVar(value=f"{due_base.hour:02d}")
        min_v = tk.StringVar(value=f"{due_base.minute:02d}")
        tk.Spinbox(d_frame, from_=0, to=23, width=3, textvariable=hour_v, format="%02.0f", bg=CELL_BG, fg=TEXT_COLOR).pack(side="left")
        tk.Label(d_frame, text=":", bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
        tk.Spinbox(d_frame, from_=0, to=59, width=3, textvariable=min_v, format="%02.0f", bg=CELL_BG, fg=TEXT_COLOR).pack(side="left", padx=(4,0))

        # buttons
        bframe = tk.Frame(cont, bg=CARD_BG)
        bframe.pack(fill="x", pady=12)
        def _save():
            new_t = title_e.get().strip()
            if new_t:
                task.title = new_t
            task.project = project_e.get().strip() or task.project
            task.priority = pr_cb.get() or task.priority
            task.description = desc.get("1.0", "end").strip()
            d = date_e.get_date()
            try:
                hh = int(hour_v.get()); mm = int(min_v.get())
            except Exception:
                hh, mm = due_base.hour, due_base.minute
            task.due = datetime(year=d.year, month=d.month, day=d.day, hour=hh, minute=mm)
            self.manager.update(task)
            dlg.destroy()
            self.refresh()
        tk.Button(bframe, text="Zapisz", command=_save, bg="#22C55E", fg="white", relief="flat", padx=12, pady=6).pack(side="right", padx=6)
        tk.Button(bframe, text="Anuluj", command=dlg.destroy, bg="#4B5563", fg="white", relief="flat", padx=12, pady=6).pack(side="right")

        title_e.focus_set()
        dlg.wait_window()

