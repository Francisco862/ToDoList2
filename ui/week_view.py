# week_view.py
import tkinter as tk
from datetime import datetime, timedelta

BG_PANEL = "#151B26"
GRID_BG = "#1B2433"
TEXT_COLOR = "#F5F5F7"

PRIORITY_COLOR = {
    "Wysoki": "#F87171",
    "Średni": "#FACC6B",
    "Niski": "#4ADE80",
    "Normal": "#9CA3AF",
}

HOURS = [f"{h:02d}:00" for h in range(24)]
DAYS = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Ndz"]


class WeekView(tk.Frame):
    def __init__(self, root, app, manager):
        super().__init__(root, bg=BG_PANEL)
        self.app = app
        self.manager = manager

        self.drag_task = None
        self.drag_tag = None
        self.last_x = 0
        self.last_y = 0

        self._build_ui()
        self.refresh()

    # ------------------------------------------------ UI
    def _build_ui(self):
        header = tk.Frame(self, bg=BG_PANEL)
        header.pack(fill="x", padx=20, pady=10)

        tk.Label(
            header,
            text="🗓️ Widok tygodnia",
            fg="white",
            bg=BG_PANEL,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        self.canvas = tk.Canvas(self, bg=GRID_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas.bind("<Configure>", lambda e: self._draw_grid())

    # ------------------------------------------------ GRID
    def _draw_grid(self):
        self.canvas.delete("grid")
        self.canvas.delete("task")

        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())

        self.col_w = w // 8
        self.row_h = h // 24

        for i in range(8):
            self.canvas.create_line(
                i * self.col_w, 0, i * self.col_w, h,
                fill="#2D3648", tags="grid"
            )

        for i, hour in enumerate(HOURS):
            y = i * self.row_h
            self.canvas.create_line(
                0, y, 8 * self.col_w, y,
                fill="#2D3648", tags="grid"
            )
            self.canvas.create_text(
                self.col_w // 2, y + self.row_h // 2,
                text=hour, fill=TEXT_COLOR, font=("Segoe UI", 9)
            )

        for i, d in enumerate(DAYS):
            self.canvas.create_text(
                (i + 1) * self.col_w + self.col_w // 2,
                15,
                text=d,
                fill="white",
                font=("Segoe UI", 11, "bold")
            )

        self._draw_tasks()

    # ------------------------------------------------ TASKS
    def _draw_tasks(self):
        for t in self.manager.tasks:
            if not t.due:
                continue

            col = t.due.weekday() + 1
            hour = t.due.hour

            x1 = col * self.col_w
            x2 = x1 + self.col_w
            y1 = hour * self.row_h
            y2 = y1 + self.row_h

            tag = f"task_{t.id}"
            color = PRIORITY_COLOR.get(t.priority, "#FACC6B")
            repeat_icon = "🔁 " if getattr(t, "repeat", None) else ""

            self.canvas.create_rectangle(
                x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                fill=color, outline="#000000",
                tags=("task", tag)
            )

            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=f"{repeat_icon}★ {t.title}",
                fill="black",
                font=("Segoe UI", 9, "bold"),
                tags=("task", tag)
            )

            self.canvas.tag_bind(tag, "<ButtonPress-1>", self._on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self._on_motion)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self._on_release)
            self.canvas.tag_bind(tag, "<Double-Button-1>",
                                 lambda e, task=t: self._open_details(task))

    # ------------------------------------------------ DRAG
    def _on_press(self, e):
        item = self.canvas.find_closest(e.x, e.y)
        tags = self.canvas.gettags(item)
        tag = next((t for t in tags if t.startswith("task_")), None)

        if not tag:
            return

        self.drag_task = next(t for t in self.manager.tasks if f"task_{t.id}" == tag)
        self.drag_tag = tag
        self.last_x = e.x
        self.last_y = e.y

    def _on_motion(self, e):
        if not self.drag_tag:
            return

        dx = e.x - self.last_x
        dy = e.y - self.last_y
        self.last_x = e.x
        self.last_y = e.y

        for item in self.canvas.find_withtag(self.drag_tag):
            self.canvas.move(item, dx, dy)

    def _on_release(self, e):
        if not self.drag_task:
            return

        bbox = self.canvas.bbox(self.drag_tag)
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2

        col = min(max(1, int(cx // self.col_w)), 7)
        hour = min(max(0, int(cy // self.row_h)), 23)

        base = self.drag_task.due
        monday = base - timedelta(days=base.weekday())

        self.drag_task.due = (monday + timedelta(days=col - 1)).replace(
            hour=hour, minute=0, second=0, microsecond=0
        )

        self.manager.update(self.drag_task)
        self.app.refresh_all_views()

        self.drag_task = None
        self.drag_tag = None

    # ------------------------------------------------ DETAILS
    def _open_details(self, task):
        dlg = tk.Toplevel(self)
        dlg.title("Szczegóły zadania")
        dlg.geometry("480x580")
        dlg.configure(bg="#0f172a")
        dlg.transient(self.winfo_toplevel())
        dlg.grab_set()

        tk.Label(
            dlg, text=task.title,
            bg="#0f172a", fg="white",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=20, pady=10)

        tk.Label(
            dlg,
            text=f"{task.project} | {task.priority}",
            bg="#0f172a", fg="#9CA3AF"
        ).pack(anchor="w", padx=20)

        tk.Label(
            dlg,
            text=task.due.strftime("%d.%m.%Y %H:%M"),
            bg="#0f172a", fg="white",
            font=("Segoe UI", 12)
        ).pack(anchor="w", padx=20, pady=10)

        repeat_var = tk.StringVar(value=task.repeat or "none")

        for txt, val in [("Brak", "none"), ("Co tydzień", "weekly"), ("Co miesiąc", "monthly")]:
            tk.Radiobutton(
                dlg, text=txt, value=val,
                variable=repeat_var,
                bg="#0f172a", fg="white",
                selectcolor="#1e293b"
            ).pack(anchor="w", padx=20)

        desc = tk.Text(dlg, bg="#111827", fg="white", height=8)
        desc.pack(fill="both", expand=True, padx=20, pady=10)
        desc.insert("1.0", task.description or "")

        def save():
            task.description = desc.get("1.0", "end-1c")
            task.repeat = repeat_var.get() if repeat_var.get() != "none" else None
            self.manager.update(task)
            self.app.refresh_all_views()
            dlg.destroy()

        dlg.protocol("WM_DELETE_WINDOW", save)

    # ------------------------------------------------ REFRESH
    def refresh(self):
        self._draw_grid()
