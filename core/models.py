from datetime import datetime
import uuid


class Task:
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = "Normal",
        due: datetime | None = None,
        status: str = "To Do",
        project: str = "General",
        tags: list[str] | None = None,

        # ✅ NOWE: POWTARZANIE
        repeat: str | None = None,   # None | "weekly" | "monthly"

        tid: str | None = None
    ):
        self.id = tid or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.due = due
        self.status = status
        self.project = project
        self.tags = tags or []

        # ✅ POWTARZANIE
        self.repeat = repeat

    # =========================
    # SERIALIZACJA
    # =========================
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due": self.due.strftime("%Y-%m-%d %H:%M") if self.due else None,
            "status": self.status,
            "project": self.project,
            "tags": self.tags,

            # ✅ ZAPIS POWTARZANIA
            "repeat": self.repeat
        }

    @staticmethod
    def from_dict(data: dict):
        due = None
        if data.get("due"):
            due = datetime.strptime(data["due"], "%Y-%m-%d %H:%M")

        return Task(
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Normal"),
            due=due,
            status=data.get("status", "To Do"),
            project=data.get("project", "General"),
            tags=data.get("tags", []),

            # ✅ BEZPIECZNIE – JEŚLI NIE MA W STARYM JSON
            repeat=data.get("repeat"),

            tid=data["id"]
        )
