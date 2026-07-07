"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care planner, based on diagrams/uml.mmd.
The Scheduler is the "brain": it retrieves tasks from an Owner's pets, orders
them by priority, and fits them into the time the owner has available.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

# How far ahead each recurrence cadence pushes a task's due date.
_RECUR_DELTAS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    scheduled_time: str | None = None  # "HH:MM" 24-hour clock, or None if unscheduled
    recurring: str = "none"  # "none" | "daily" | "weekly"
    due_date: date | None = None  # the day this instance is due
    completed: bool = False

    _PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more important)."""
        return self._PRIORITY_WEIGHTS.get(self.priority.lower(), 2)

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy of this task on its next due date.

        Uses ``timedelta`` to advance the due date by one day ("daily") or one
        week ("weekly"). If the task has no due date yet, we count from today.
        Returns ``None`` for non-recurring tasks so callers can simply check the
        result before scheduling a follow-up.
        """
        delta = _RECUR_DELTAS.get(self.recurring)
        if delta is None:
            return None
        base = self.due_date or date.today()
        return replace(self, due_date=base + delta, completed=False)

    def start_minutes(self) -> int | None:
        """Return the start time as minutes-since-midnight, or None if unscheduled."""
        if not self.scheduled_time:
            return None
        hours, minutes = self.scheduled_time.split(":")
        return int(hours) * 60 + int(minutes)

    def end_minutes(self) -> int | None:
        """Return the end time (start + duration) as minutes-since-midnight."""
        start = self.start_minutes()
        return None if start is None else start + self.duration_minutes


@dataclass
class Pet:
    """The animal being cared for and its associated tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and auto-schedule its next occurrence.

        For a recurring task this appends a fresh instance (advanced by one day
        or week via :meth:`Task.next_occurrence`) so the chore reappears on its
        next due date. Returns the newly created follow-up task, or ``None`` if
        the task was one-off.
        """
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            self.add_task(follow_up)
        return follow_up


@dataclass
class Owner:
    """The pet owner using PawPal+."""

    name: str
    minutes_available: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def set_availability(self, minutes: int) -> None:
        """Set how many minutes the owner has for care today."""
        self.minutes_available = minutes

    def get_all_tasks(self) -> list[Task]:
        """Collect the care tasks from every pet this owner has.

        This is how the Scheduler "talks to" the Owner: it asks for a single
        flat list of tasks instead of reaching into each Pet itself.
        """
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def filter_tasks(
        self, pet_name: str | None = None, status: str | None = None
    ) -> list[Task]:
        """Return tasks narrowed by pet and/or completion status.

        pet_name: keep only tasks belonging to the pet with this name (None = any).
        status:   "completed" or "pending" (None = any).
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            names = {pet.name for pet in self.pets if pet.name == pet_name}
            tasks = [
                t
                for pet in self.pets
                if pet.name in names
                for t in pet.tasks
            ]
        if status == "completed":
            tasks = [t for t in tasks if t.completed]
        elif status == "pending":
            tasks = [t for t in tasks if not t.completed]
        return tasks


class Scheduler:
    """Builds and explains a daily care plan from a set of tasks."""

    def __init__(self, tasks: list[Task], minutes_available: int) -> None:
        self.tasks = tasks
        self.minutes_available = minutes_available

    @classmethod
    def from_owner(cls, owner: Owner) -> "Scheduler":
        """Build a Scheduler from an Owner's pets and availability.

        This is the intended entry point: the Owner knows its pets and its
        time budget, so the Scheduler simply asks the Owner for both.
        """
        return cls(owner.get_all_tasks(), owner.minutes_available)

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (high first), shorter tasks breaking ties."""
        return sorted(
            self.tasks,
            key=lambda task: (-task.priority_score(), task.duration_minutes),
        )

    def sort_by_time(self) -> list[Task]:
        """Return scheduled tasks in chronological order.

        Unscheduled tasks (no start time) are pushed to the end but kept.
        """
        return sorted(
            self.tasks,
            key=lambda task: (
                task.start_minutes() is None,  # False (0) sorts before True (1)
                task.start_minutes() or 0,
            ),
        )

    def find_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time ranges overlap.

        Uses a sweep-line approach: sort scheduled tasks by start time, then
        compare each task's end against the next task's start. Two tasks
        conflict when one starts before the other ends.
        """
        scheduled = [t for t in self.sort_by_time() if t.start_minutes() is not None]
        conflicts: list[tuple[Task, Task]] = []
        for earlier, later in zip(scheduled, scheduled[1:]):
            if later.start_minutes() < earlier.end_minutes():
                conflicts.append((earlier, later))
        return conflicts

    def filter_by_time(self) -> list[Task]:
        """Return the highest-priority tasks that together fit the available minutes."""
        remaining = self.minutes_available
        fitted: list[Task] = []
        for task in self.sort_by_priority():
            if task.duration_minutes <= remaining:
                fitted.append(task)
                remaining -= task.duration_minutes
        return fitted

    def build_plan(self) -> list[Task]:
        """Produce the final ordered daily plan based on constraints."""
        return self.filter_by_time()

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        plan = self.build_plan()
        if not plan:
            return (
                f"No tasks fit within {self.minutes_available} minutes. "
                "Free up more time or shorten some tasks."
            )

        used = sum(task.duration_minutes for task in plan)
        lines = [
            f"Daily plan ({used} of {self.minutes_available} minutes used):",
        ]
        for i, task in enumerate(plan, start=1):
            lines.append(
                f"  {i}. {task.title} — {task.priority} priority, "
                f"{task.duration_minutes} min"
            )

        skipped = [task for task in self.tasks if task not in plan]
        if skipped:
            lines.append("Skipped (not enough time):")
            for task in skipped:
                lines.append(f"  - {task.title} ({task.duration_minutes} min)")

        conflicts = self.find_conflicts()
        if conflicts:
            lines.append("⚠️ Time conflicts:")
            for earlier, later in conflicts:
                lines.append(
                    f"  - '{earlier.title}' ({earlier.scheduled_time}) overlaps "
                    f"'{later.title}' ({later.scheduled_time})"
                )

        return "\n".join(lines)
