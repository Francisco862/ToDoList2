import json
import os
from core.models import Task



class Storage:
    FILE = "tasks.json"

    def load(self) -> list[Task]:
        if not os.path.exists(self.FILE):
            return []

        with open(self.FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(t) for t in data]

    def save(self, tasks: list[Task]):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=4, ensure_ascii=False)
