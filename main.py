"""Demo script for the PawPal+ system.

A quick "testing ground" to verify the logic in pawpal_system.py works
end-to-end from the terminal.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # Create an owner with a limited amount of time today.
    owner = Owner(name="Alex", minutes_available=60)

    # Create at least two pets.
    rex = Pet(name="Rex", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    owner.add_pet(rex)
    owner.add_pet(whiskers)

    # Add at least three tasks with different durations and priorities.
    rex.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))
    rex.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high"))
    whiskers.add_task(Task(title="Clean litter box", duration_minutes=15, priority="medium"))
    whiskers.add_task(Task(title="Play time", duration_minutes=20, priority="low"))

    # Build today's schedule from the owner's pets and availability.
    scheduler = Scheduler.from_owner(owner)

    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain())


if __name__ == "__main__":
    main()
