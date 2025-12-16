import tkinter as tk
import calendar
from datetime import datetime, date
from core.manager import TaskManager

BG_PANEL = "#151B26"
CELL_BG = "#1B2433"
TEXT_COLOR = "#F5F5F7"
ACCENT = "#2563EB"


class CalendarView(tk.Frame):
    def __init__(self, master, manager: TaskManager, app, **kwargs):
        super().__init__(master, bg=BG_PANEL, **kwargs)
        self.manager = manager
        self.app = app

        today = date.today()
        self.current_year = today.year
        self.current_month = today.month

        self.day_labels = []  # referencje do komórek

        self._build_ui()
        self.refresh()

    # ---------- SHOW / HIDE ----------

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()

    # ---------- UI ----------

    def _build_ui(self):
        # GÓRNY PASEK: nawigacja po miesiącach
        header = tk.Frame(self, bg=BG_PANEL)
        header.pack(fill="x", pady=10)

        prev_btn = tk.Button(
            header,
            text="◀",
            command=self.prev_month,
            bg=BG_PANEL,
            fg=TEXT_COLOR,
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            width=3,
        )
        prev_btn.pack(side="left", padx=10)

        self.month_label = tk.Label(
            header,
            text="",
            bg=BG_PANEL,
            fg=TEXT_COLOR,
            font=("Segoe UI", 16, "bold"),
        )
        self.month_label.pack(side="left", padx=10)

        next_btn = tk.Button(
            header,
            text="▶",
            command=self.next_month,
            bg=BG_PANEL,
            fg=TEXT_COLOR,
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            width=3,
        )
        next_btn.pack(side="left")

        # główna siatka
        self.grid_frame = tk.Frame(self, bg=BG_PANEL)
        self.grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # nazwy dni tygodnia (Pon–Ndz)
        self.weekdays = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]
        for col, d in enumerate(self.weekdays):
            tk.Label(
                self.grid_frame,
                text=d,
                bg=BG_PANEL,
                fg=TEXT_COLOR,
                font=("Segoe UI", 11, "bold"),
            ).grid(row=0, column=col, sticky="nsew", pady=(0, 5))

        # 6 wierszy po 7 kolumn – typowy kalendarz
        for r in range(1, 7):
            row_cells = []
            for c in range(7):
                cell = tk.Frame(self.grid_frame, bg=CELL_BG, bd=1, relief="solid")
                cell.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)

                day_label = tk.Label(
                    cell,
                    text="",
                    bg=CELL_BG,
                    fg=TEXT_COLOR,
                    anchor="nw",
                    font=("Segoe UI", 10, "bold"),
                )
                day_label.pack(anchor="nw", padx=4, pady=2)

                tasks_label = tk.Label(
                    cell,
                    text="",
                    bg=CELL_BG,
                    fg="#D1D5DB",
                    justify="left",
                    anchor="nw",
                    font=("Segoe UI", 9),
                    wraplength=120,
                )
                tasks_label.pack(fill="both", expand=True, padx=4, pady=(0, 4))

                row_cells.append((day_label, tasks_label))
            self.day_labels.append(row_cells)

        # rozciąganie
        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)
        for r in range(1, 7):
            self.grid_frame.rowconfigure(r, weight=1)

    # ---------- LOGIKA ODSWIEŻANIA ----------

    def refresh(self):
        # --- polskie nazwy miesięcy ---
        POLISH_MONTHS = {
            1: "Styczeń",
            2: "Luty",
            3: "Marzec",
            4: "Kwiecień",
            5: "Maj",
            6: "Czerwiec",
            7: "Lipiec",
            8: "Sierpień",
            9: "Wrzesień",
            10: "Październik",
            11: "Listopad",
            12: "Grudzień",
        }

        month_name = POLISH_MONTHS.get(self.current_month, "")
        self.month_label.config(text=f"{month_name} {self.current_year}")

        # dane kalendarza
        cal = calendar.Calendar(firstweekday=0)  # 0 = Monday
        month_days = list(cal.itermonthdates(self.current_year, self.current_month))

        # tasks z due w tym miesiącu
        tasks_by_day: dict[int, list[str]] = {}
        for t in self.manager.tasks:
            if getattr(t, "due", None):
                d = t.due.date()
                if d.year == self.current_year and d.month == self.current_month:
                    tasks_by_day.setdefault(d.day, []).append(t.title)

        # wyczyść komórki
        for r in range(6):
            for c in range(7):
                day_lbl, tasks_lbl = self.day_labels[r][c]
                day_lbl.config(text="", fg=TEXT_COLOR, bg=CELL_BG)
                tasks_lbl.config(text="", bg=CELL_BG)

        # wypełnij komórki
        idx = 0
        for r in range(6):
            for c in range(7):
                if idx >= len(month_days):
                    continue
                d = month_days[idx]
                day_lbl, tasks_lbl = self.day_labels[r][c]

                if d.month == self.current_month:
                    day_lbl.config(text=str(d.day))
                    # zadania w tym dniu
                    titles = tasks_by_day.get(d.day, [])
                    if titles:
                        # max 2 linie + „+N”
                        shown = titles[:2]
                        extra = len(titles) - len(shown)
                        text = "\n".join(shown)
                        if extra > 0:
                            text += f"\n+{extra} więcej…"
                        tasks_lbl.config(text=text)
                    else:
                        tasks_lbl.config(text="")
                else:
                    # dni z poprzedniego / następnego miesiąca – wyszarzone
                    day_lbl.config(text=str(d.day), fg="#6B7280")
                    tasks_lbl.config(text="")

                idx += 1

    # ---------- NAWIGACJA ----------

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh()
