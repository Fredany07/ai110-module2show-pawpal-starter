# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample output from running `python main.py`:

```
========================================
Today's Schedule for Alex
========================================
Daily plan (55 of 60 minutes used):
  1. Feed breakfast — high priority, 10 min
  2. Morning walk — high priority, 30 min
  3. Clean litter box — medium priority, 15 min
Skipped (not enough time):
  - Play time (20 min)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 7 items

tests/test_pawpal.py .......                                             [100%]

============================== 7 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

Phase 3 adds four algorithmic features to the logic layer (`pawpal_system.py`):

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Priority-first (high → low, shorter tasks break ties) *or* chronological by `scheduled_time`; unscheduled tasks sort last. |
| Filtering | `Owner.filter_tasks(pet_name, status)`, `Scheduler.filter_by_time()` | Narrow the task list by pet and/or completion status (`pending`/`completed`); `filter_by_time()` greedily fits the highest-priority tasks into the available minutes. |
| Conflict handling | `Scheduler.find_conflicts()` | Sweep-line overlap check: sorts by start time and flags any task whose window overlaps its neighbor's. Returns warning pairs instead of raising. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task auto-creates a fresh instance whose `due_date` is advanced with `timedelta` (today + 1 day / + 1 week). |

### Sorting behavior
- **By priority** — `Scheduler.sort_by_priority()`
- **By time** — `Scheduler.sort_by_time()` (lambda key over `Task.start_minutes()`)

### Filtering behavior
- **By pet or completion status** — `Owner.filter_tasks(pet_name=..., status=...)`

### Conflict detection logic
- **Overlapping time slots** — `Scheduler.find_conflicts()`

### Recurring task logic
- **Daily / weekly regeneration on completion** — `Pet.complete_task()` → `Task.next_occurrence()`

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
