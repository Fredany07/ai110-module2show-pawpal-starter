"""PawPal+ logic layer.

Backend classes for the PawPal+ pet care planner, based on diagrams/uml.mmd.
This is a skeleton: attributes are defined, but method bodies are stubs to be
implemented in a later phase.
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

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority (higher = more important)."""
        raise NotImplementedError


@dataclass
class Pet:
    """The animal being cared for and its associated tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner using PawPal+."""

    name: str
    minutes_available: int = 0
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError

    def set_availability(self, minutes: int) -> None:
        """Set how many minutes the owner has for care today."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily care plan from a set of tasks."""

    def __init__(self, tasks: list[Task], minutes_available: int) -> None:
        self.tasks = tasks
        self.minutes_available = minutes_available

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (and secondary criteria)."""
        raise NotImplementedError

    def filter_by_time(self) -> list[Task]:
        """Return only the tasks that fit within the available minutes."""
        raise NotImplementedError

    def build_plan(self) -> list[Task]:
        """Produce the final ordered daily plan based on constraints."""
        raise NotImplementedError

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        raise NotImplementedError
