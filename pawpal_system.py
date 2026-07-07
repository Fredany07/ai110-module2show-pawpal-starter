"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care planner, based on diagrams/uml.mmd.
The Scheduler is the "brain": it retrieves tasks from an Owner's pets, orders
them by priority, and fits them into the time the owner has available.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    recurring: bool = False
    completed: bool = False

    _PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3}

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more important)."""
        return self._PRIORITY_WEIGHTS.get(self.priority.lower(), 2)

    def mark_complete(self) -> None:
        """Mark this task as done for the day."""
        self.completed = True


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

        return "\n".join(lines)
