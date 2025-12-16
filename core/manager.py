from datetime import datetime, timedelta
from core.models import Task
from core.storage import Storage
import sys
import os



class TaskManager:

    def resource_path(filename):
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), filename)
        return os.path.join(os.path.dirname(__file__), "..", filename)

    def __init__(self):
        self.storage = Storage()
        self.tasks: list[Task] = self.storage.load()

    # ✅ ---- CRUD ----

    def add(self, task: Task):
        self.tasks.append(task)
        self.save()

    def delete(self, tid: str):
        self.tasks = [t for t in self.tasks if t.id != tid]
        self.save()

    def update(self, task: Task):
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                break
        self.save()

    def get_task(self, tid: str):
        for t in self.tasks:
            if t.id == tid:
                return t
        return None

    def mark_done(self, tid: str):
        task = self.get_task(tid)
        if task:
            task.status = "Done"
            self.save()

    # ✅ ---- FILTRY ----

    def by_project(self, project: str):
        return [t for t in self.tasks if t.project == project]

    def by_status(self, status: str):
        return [t for t in self.tasks if t.status == status]

    def get_tasks_for_week(self, date: datetime):
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=7)
        return [t for t in self.tasks if t.due and start <= t.due < end]

    # ✅ ---- SAVE ----

    def save(self):
        self.storage.save(self.tasks)
