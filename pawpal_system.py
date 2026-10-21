from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


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
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Build the next occurrence of a recurring task.

        Looks up the frequency in RECURRENCE_DAYS and adds that many days
        (via timedelta) to this task's due_date, so a late completion still
        advances from the original due date.

        Returns:
            A new, uncompleted copy of this task, or None if the frequency
            is not "daily" or "weekly".
        """
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + timedelta(days=days))


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

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete; if daily/weekly, add the next occurrence to its pet.

        Returns the newly created task, or None for one-off tasks.
        """
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is None:
            return None
        pet = next(p for p in self.owner.pets if p.name == task.pet_name)
        pet.add_task(nxt)
        return nxt

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by their "HH:MM" time, earliest first.

        Args:
            tasks: Tasks to sort; defaults to every task across all pets.

        Returns:
            A new sorted list. The sort is stable, so tasks at the same time
            keep their original order. Zero-padded 24-hour strings sort
            correctly as plain text.
        """
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Sort tasks by priority (high, medium, low), then by time.

        Args:
            tasks: Tasks to sort; defaults to every task across all pets.

        Returns:
            A new sorted list. Unknown priority values sort last.
        """
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.time))

    def filter_tasks(self, completed: bool | None = None,
                     pet_name: str | None = None) -> list[Task]:
        """Filter all tasks by completion status and/or pet name in one pass.

        Args:
            completed: True for finished tasks, False for pending ones,
                None to ignore completion status.
            pet_name: Keep only this pet's tasks, or None for every pet.

        Returns:
            A new list of the tasks matching every filter that was given.
        """
        return [
            t for t in self.get_all_tasks()
            if (completed is None or t.completed == completed)
            and (pet_name is None or t.pet_name == pet_name)
        ]

    def find_conflicts(self, same_pet: bool | None = None) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks due the same day at the same time.

        same_pet=True  -> only pairs for the same pet
        same_pet=False -> only pairs across different pets
        same_pet=None  -> both (default)
        """
        pending = self.sort_by_time(self.filter_tasks(completed=False))
        return [
            (a, b)
            for i, a in enumerate(pending)
            for b in pending[i + 1:]
            if a.time == b.time
            and a.due_date == b.due_date
            and (same_pet is None or (a.pet_name == b.pet_name) == same_pet)
        ]

    def conflict_warnings(self) -> list[str]:
        """Turn each conflicting pair from find_conflicts into a message.

        Each message names the time, date, whether the clash is for the
        same pet or different pets, and both tasks. Only reports; it never
        raises or changes any task.

        Returns:
            A list of warning strings, empty if there are no conflicts.
        """
        warnings = []
        for a, b in self.find_conflicts():
            kind = "same pet" if a.pet_name == b.pet_name else "different pets"
            warnings.append(
                f"Conflict at {a.time} on {a.due_date} ({kind}): "
                f"{a.pet_name}'s '{a.description}' and {b.pet_name}'s '{b.description}'"
            )
        return warnings

    def conflict_warning_for(self, task: Task) -> str | None:
        """Lightweight check: warn if another pending task shares this task's slot.

        Compares the task's time and due_date against every other pending
        task (any pet) in a single pass. It only reports, so callers can
        still keep the task and the program never crashes on a conflict.

        Args:
            task: The task to check, usually one that was just added.

        Returns:
            A warning message naming the clashing tasks, or None if clear.
        """
        clashes = [
            t for t in self.get_all_tasks()
            if t is not task and not t.completed
            and t.time == task.time and t.due_date == task.due_date
        ]
        if not clashes:
            return None
        names = ", ".join(f"{t.pet_name}'s '{t.description}'" for t in clashes)
        return f"Warning: '{task.description}' at {task.time} overlaps with {names}."

    def build_daily_plan(self) -> list[Task]:
        """Choose today's tasks with a greedy, priority-first selection.

        Considers pending tasks due today or earlier, ordered by priority
        then time, and keeps each one that still fits in the owner's
        available_minutes. Tasks that do not fit are skipped.

        Returns:
            The chosen tasks sorted by time of day.
        """
        chosen: list[Task] = []
        used = 0
        today = date.today()
        pending = [t for t in self.filter_tasks(completed=False) if t.due_date <= today]
        for task in self.sort_by_priority(pending):
            if used + task.duration_minutes <= self.owner.available_minutes:
                chosen.append(task)
                used += task.duration_minutes
        return self.sort_by_time(chosen)

    def explain_plan(self) -> list[str]:
        """Describe the daily plan as one readable line per task.

        Returns:
            Strings like "08:00 - Biscuit: Morning walk (30 min, high
            priority)", in time order, one for each task from
            build_daily_plan.
        """
        plan = self.build_daily_plan()
        return [
            f"{t.time} - {t.pet_name}: {t.description} "
            f"({t.duration_minutes} min, {t.priority} priority)"
            for t in plan
        ]
