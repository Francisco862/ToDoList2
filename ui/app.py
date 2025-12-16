import tkinter as tk

from core.manager import TaskManager
from ui.sidebar import Sidebar
from ui.list_view import ListView
from ui.week_view import WeekView
from ui.calendar_view import CalendarView


class TodoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("To-Do PRO – ClickUp style")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#0f172a")

        # ------------------ MODEL ------------------
        self.task_manager = TaskManager()

        # ------------------ UKŁAD OKNA ------------------
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        # PANEL LEWY — SIDEBAR
        self.sidebar = Sidebar(self.root, self)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # PANEL PRAWY — miejsce na widoki
        self.main_frame = tk.Frame(self.root, bg="#020617")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.content_frame = tk.Frame(self.main_frame, bg="#020617")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # ------------------ WIDOKI ------------------
        self.list_view = ListView(self.content_frame, self.task_manager)
        self.week_view = WeekView(self.content_frame, self, self.task_manager)
        self.calendar_view = CalendarView(self.content_frame, self.task_manager, self)

        for v in (self.list_view, self.week_view, self.calendar_view):
            v.grid(row=0, column=0, sticky="nsew")

        self.current_view = None
        self.show("list")

    # -------------------------------------------------
    # PRZEŁĄCZANIE WIDOKÓW
    # -------------------------------------------------
    def show(self, view_name: str):
        """Ukryj wszystko i pokaż wybrany widok."""

        self.list_view.grid_remove()
        self.week_view.grid_remove()
        self.calendar_view.grid_remove()

        if view_name == "list":
            self.list_view.grid()
            self.current_view = "list"

        elif view_name == "week":
            self.week_view.grid()
            self.current_view = "week"

        elif view_name == "calendar":
            self.calendar_view.grid()
            self.current_view = "calendar"

        # aktualizuj opis w sidebar
        try:
            self.sidebar.set_current(view_name.capitalize())
        except:
            pass

    # -------------------------------------------------
    # GLOBALNE ODŚWIEŻENIE APLIKACJI
    # -------------------------------------------------
    def refresh_all_views(self):
        """Odświeża WSZYSTKIE widoki po zmianie danych."""
        try:
            self.list_view.refresh()
        except:
            pass

        try:
            self.week_view.refresh()
        except:
            pass

        try:
            self.calendar_view.refresh()
        except:
            pass
