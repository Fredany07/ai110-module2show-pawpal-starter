"""Quick tests for core PawPal+ behaviors."""

from pawpal_system import Pet, Task


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
