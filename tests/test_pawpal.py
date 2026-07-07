"""Quick tests for core PawPal+ behaviors."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() should flip a task's completed status to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high")

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet(name="Rex", species="dog")

    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feed breakfast", duration_minutes=10))

    assert len(pet.tasks) == 1


def test_sort_by_time_orders_chronologically():
    """sort_by_time() should order scheduled tasks by start time, unscheduled last."""
    late = Task(title="Evening walk", duration_minutes=20, scheduled_time="18:00")
    early = Task(title="Morning walk", duration_minutes=20, scheduled_time="07:00")
    unscheduled = Task(title="Grooming", duration_minutes=15)

    scheduler = Scheduler(tasks=[late, unscheduled, early], minutes_available=120)

    assert scheduler.sort_by_time() == [early, late, unscheduled]


def test_filter_tasks_by_pet_and_status():
    """filter_tasks() should narrow by pet name and completion status."""
    owner = Owner(name="Alex")
    rex = Pet(name="Rex", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    owner.add_pet(rex)
    owner.add_pet(cat)

    done = Task(title="Feed", duration_minutes=10, completed=True)
    pending = Task(title="Walk", duration_minutes=30)
    rex.add_task(done)
    rex.add_task(pending)
    cat.add_task(Task(title="Litter", duration_minutes=15))

    assert owner.filter_tasks(pet_name="Rex") == [done, pending]
    assert owner.filter_tasks(status="pending") == [pending, cat.tasks[0]]
    assert owner.filter_tasks(pet_name="Rex", status="completed") == [done]


def test_find_conflicts_detects_overlap():
    """find_conflicts() should flag tasks whose time ranges overlap."""
    walk = Task(title="Walk", duration_minutes=60, scheduled_time="08:00")   # 08:00–09:00
    vet = Task(title="Vet", duration_minutes=30, scheduled_time="08:30")     # overlaps
    play = Task(title="Play", duration_minutes=30, scheduled_time="10:00")   # no overlap

    scheduler = Scheduler(tasks=[walk, vet, play], minutes_available=240)
    conflicts = scheduler.find_conflicts()

    assert conflicts == [(walk, vet)]


def test_completing_recurring_task_schedules_next_occurrence():
    """Completing a daily task should append a fresh instance due one day later."""
    pet = Pet(name="Rex", species="dog")
    feed = Task(
        title="Feed",
        duration_minutes=10,
        recurring="daily",
        due_date=date(2026, 7, 7),
    )
    pet.add_task(feed)

    follow_up = pet.complete_task(feed)

    assert feed.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.due_date == date(2026, 7, 8)  # today + 1 day via timedelta
    assert len(pet.tasks) == 2


def test_completing_one_off_task_creates_no_follow_up():
    """Completing a non-recurring task should not create a new instance."""
    pet = Pet(name="Rex", species="dog")
    vet = Task(title="Vet visit", duration_minutes=45)
    pet.add_task(vet)

    follow_up = pet.complete_task(vet)

    assert vet.completed is True
    assert follow_up is None
    assert len(pet.tasks) == 1
