# core/reminders.py
import time
import threading
from datetime import datetime
from core.manager import TaskManager

class ReminderService:
    """
    Prosty serwis przypomnień uruchamiany w osobnym wątku.
    Sprawdza zadania w TaskManager i drukuje przypomnienie w konsoli
    jeśli zadanie ma termin ('due') w ciągu najbliższej minuty.
    """

    def __init__(self, manager: TaskManager):
        self.manager = manager
        self.notified = set()
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True, name="reminder-loop")
        self.thread.start()

    def _loop(self):
        while self.running:
            now = datetime.now()
            for t in self.manager.tasks:
                # jeżeli brak terminu — pomijamy
                if not getattr(t, "due", None):
                    continue

                # jeżeli zadanie ukończone — pomijamy (status "Done")
                if getattr(t, "status", None) == "Done":
                    continue

                # ile sekund do terminu
                try:
                    delta = (t.due - now).total_seconds()
                except Exception:
                    # nieprawidłowy typ w t.due — pomiń
                    continue

                # jeśli termin za <60s i >0s i jeszcze nie powiadomiono
                if 0 < delta < 60 and t.id not in self.notified:
                    # tutaj możesz zastąpić print prawdziwym popupem w UI
                    print(f"🔔 PRZYPOMNIENIE: {t.title} — termin za {int(delta)}s")
                    self.notified.add(t.id)

            time.sleep(10)

    def stop(self):
        self.running = False
        # opcjonalnie dołącz wątek
        try:
            if self.thread.is_alive():
                self.thread.join(timeout=1.0)
        except Exception:
            pass
