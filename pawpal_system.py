from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """A single care activity."""
    description: str
    time: str                         # "HH:MM", 24-hour
    frequency: str = "once"           # "once", "daily", "weekly"
    duration_minutes: int = 15
    priority: str = "medium"          # "low", "medium", "high"
    completed: bool = False
    pet_name: str = ""                # set by Pet.add_task

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the tasks that belong to it."""
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and record the pet's name on it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return this pet's tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """An owner who manages multiple pets."""
    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet, together."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads tasks through the given owner."""
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across the owner's pets via Owner.get_all_tasks."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return the given tasks (default: all) sorted by time of day."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return the given tasks (default: all) sorted by priority, then time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.time))

    def filter_tasks(self, completed: bool | None = None,
                     pet_name: str | None = None) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name."""
        tasks = self.get_all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        return tasks

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks scheduled at the same time."""
        pending = self.sort_by_time(self.filter_tasks(completed=False))
        return [
            (a, b)
            for i, a in enumerate(pending)
            for b in pending[i + 1:]
            if a.time == b.time
        ]

    def build_daily_plan(self) -> list[Task]:
        """Pick pending tasks by priority within the owner's time, in time order."""
        chosen: list[Task] = []
        used = 0
        for task in self.sort_by_priority(self.filter_tasks(completed=False)):
            if used + task.duration_minutes <= self.owner.available_minutes:
                chosen.append(task)
                used += task.duration_minutes
        return self.sort_by_time(chosen)

    def explain_plan(self) -> list[str]:
        """Return one readable line per task in the daily plan."""
        plan = self.build_daily_plan()
        return [
            f"{t.time} - {t.pet_name}: {t.description} "
            f"({t.duration_minutes} min, {t.priority} priority)"
            for t in plan
        ]
