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

    # Add tasks with times so we can sort chronologically and spot conflicts.
    rex.add_task(
        Task(title="Morning walk", duration_minutes=30, priority="high",
             scheduled_time="08:00", recurring="daily")
    )
    rex.add_task(
        Task(title="Feed breakfast", duration_minutes=10, priority="high",
             scheduled_time="08:15")  # overlaps the walk on purpose
    )
    whiskers.add_task(
        Task(title="Clean litter box", duration_minutes=15, priority="medium",
             scheduled_time="09:00")
    )
    whiskers.add_task(
        Task(title="Play time", duration_minutes=20, priority="low",
             scheduled_time="10:00")
    )

    # Build today's schedule from the owner's pets and availability.
    scheduler = Scheduler.from_owner(owner)

    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(scheduler.explain())

    print("\nChronological order:")
    for task in scheduler.sort_by_time():
        print(f"  {task.scheduled_time or '  —  '}  {task.title}")

    print("\nPending tasks for Rex:")
    for task in owner.filter_tasks(pet_name="Rex", status="pending"):
        print(f"  - {task.title}")

    print("\nRecurring task auto-reschedules on completion:")
    walk = rex.tasks[0]  # the daily "Morning walk"
    print(f"  Completing '{walk.title}' (recurring={walk.recurring})...")
    follow_up = rex.complete_task(walk)
    if follow_up is not None:
        print(f"  -> new instance created, due {follow_up.due_date}")


if __name__ == "__main__":
    main()
