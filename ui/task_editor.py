import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
from core.models import Task
from core.manager import TaskManager

class TaskEditor(tk.Toplevel):
    def __init__(self, master, manager: TaskManager, task: Task = None, callback=None, dark_mode=False):
        super().__init__(master)
        self.manager = manager
        self.task = task
        self.callback = callback  # funkcja do odświeżenia widoku listy po zapisaniu
        self.dark_mode = dark_mode

        self.title("Edytuj Zadanie" if task else "Nowe Zadanie")
        self.geometry("400x400")
        self.resizable(False, False)

        self._build_ui()
        if task:
            self._populate_fields(task)

    def _build_ui(self):
        bg = "#222" if self.dark_mode else "#f4f4f4"
        fg = "white" if self.dark_mode else "black"
        self.config(bg=bg)

        # Tekst zadania
        tk.Label(self, text="Opis zadania:", bg=bg, fg=fg).pack(pady=5, anchor="w", padx=10)
        self.text_entry = tk.Entry(self, width=40)
        self.text_entry.pack(pady=5, padx=10)

        # Priorytet
        tk.Label(self, text="Priorytet:", bg=bg, fg=fg).pack(pady=5, anchor="w", padx=10)
        self.priority = ttk.Combobox(self, values=["Wysoki", "Średni", "Niski"], state="readonly", width=15)
        self.priority.set("Średni")
        self.priority.pack(pady=5, padx=10)

        # Kategoria
        tk.Label(self, text="Kategoria:", bg=bg, fg=fg).pack(pady=5, anchor="w", padx=10)
        self.category = ttk.Combobox(self, values=["Ogólne", "Praca", "Szkoła", "Dom"], state="readonly", width=20)
        self.category.set("Ogólne")
        self.category.pack(pady=5, padx=10)

        # Data
        tk.Label(self, text="Data:", bg=bg, fg=fg).pack(pady=5, anchor="w", padx=10)
        self.cal = Calendar(self, selectmode="day", date_pattern="yyyy-mm-dd", locale="pl_PL")
        self.cal.pack(pady=5, padx=10)

        # Godzina
        time_frame = tk.Frame(self, bg=bg)
        time_frame.pack(pady=5)
        tk.Label(time_frame, text="Godzina:", bg=bg, fg=fg).pack(side="left")
        self.hour_var = tk.StringVar(value="12")
        self.hour_spin = tk.Spinbox(time_frame, from_=0, to=23, width=3, textvariable=self.hour_var, format="%02.0f")
        self.hour_spin.pack(side="left", padx=5)
        tk.Label(time_frame, text="Minuta:", bg=bg, fg=fg).pack(side="left")
        self.minute_var = tk.StringVar(value="00")
        self.minute_spin = tk.Spinbox(time_frame, from_=0, to=59, width=3, textvariable=self.minute_var, format="%02.0f")
        self.minute_spin.pack(side="left", padx=5)

        # Przycisk zapisu
        self.save_btn = ttk.Button(self, text="Zapisz", command=self.save_task)
        self.save_btn.pack(pady=15)

    def _populate_fields(self, task: Task):
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, task.text)
        self.priority.set(task.priority)
        self.category.set(task.category)
        self.cal.set_date(task.date_time.strftime("%Y-%m-%d"))
        self.hour_var.set(f"{task.date_time.hour:02d}")
        self.minute_var.set(f"{task.date_time.minute:02d}")

    def save_task(self):
        text = self.text_entry.get().strip()
        if not text:
            tk.messagebox.showerror("Błąd", "Opis zadania nie może być pusty!")
            return

        dt = datetime.strptime(self.cal.get_date(), "%Y-%m-%d")
        dt = dt.replace(hour=int(self.hour_var.get()), minute=int(self.minute_var.get()))

        if self.task:  # edycja istniejącego
            self.task.text = text
            self.task.priority = self.priority.get()
            self.task.category = self.category.get()
            self.task.date_time = dt
            self.task.date = dt.strftime("%Y-%m-%d")
        else:  # nowe zadanie
            new_task = Task(text=text,
                            priority=self.priority.get(),
                            date=dt,
                            category=self.category.get())
            self.manager.add(new_task)

        self.manager.save()
        if self.callback:
            self.callback()
        self.destroy()
