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

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like (from `python main.py`):

```text
Today's Schedule for Sam (90 min available)
============================================================
08:00 - Biscuit: Morning walk (30 min, high priority)
08:00 - Mia: Playtime (15 min, medium priority)
08:30 - Mia: Breakfast (10 min, high priority)
12:00 - Mia: Give medication (5 min, high priority)
18:00 - Biscuit: Evening walk (30 min, medium priority)

Conflicts:
  WARNING: Conflict at 08:00 on 2026-10-20 (different pets): Biscuit's 'Morning walk' and Mia's 'Playtime'
```

## 🧪 Testing PawPal+

Run the command from the project root:
```bash
python -m pytest
```

**What the tests cover** (20 tests in `tests/test_pawpal.py`):

- **Task and pet basics:** marking a task complete, and adding a task to a pet.
- **Sorting:** tasks come back in chronological order across pets, equal times keep their original order, the original list is not mutated, an empty list works, and priority sorting puts high first (then time) with unknown priorities last.
- **Recurring tasks:** completing a daily task creates a new one due the next day, weekly tasks are due 7 days later, one-off tasks do not repeat, and rollovers across month end, year end, and leap day are correct. The copy is independent, unknown frequencies are ignored, and future occurrences stay out of today's plan.
- **Conflict detection:** duplicate start times are flagged for the same pet and for different pets, different times or days are not flagged, completed tasks are ignored, and `conflict_warning_for` returns a message instead of raising an error.


```
tests/test_pawpal.py ....................                                                                      [100%]

================================================= 20 passed in 0.04s ================================================
```

**Confidence level: ⭐⭐⭐⭐ (4/5)**

All 20 tests pass, and they cover the main behaviors, including sorting, recurrence, and conflict detection. One star is held back because of the known gap that conflicts only match exact start times (durations that overlap are not detected). Also, completing the same recurring task twice creates a duplicate next occurrence.

## Implementation Summary
I made pawpal_system.py have the four required classes: Task, Pet, Owner, and Scheduler, as the original design used five. The Task class stores care activity details and completion status, while Pet manages its own tasks. Owner holds multiple pets and provides their combined tasks through get_all_tasks(). Scheduler uses this method to select pending tasks by priority that fit within the owner’s available time, then displays them in time order. It also supports filtering and flags tasks with identical start times. I added a demo in main.py and tests in test_pawpal.py for marking a task complete and adding a task to a pet.

## ✨ Features

- **Sorting:** by time ("HH:MM", earliest first) or by priority (high, medium, low, ties by time).
- **Filtering:** by completion status and/or pet.
- **Conflict warnings:** flags pending tasks with the same date and start time. It only warns and never blocks a task.
- **Daily/weekly recurrence:** completing a recurring task adds the next copy, due 1 or 7 days after the original due date.
- **Daily plan:** greedily picks pending tasks due today or earlier by priority until `available_minutes` runs out, shown in time order with a one-line explanation per task.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Sorts by start time or priority (high, medium, low), with time used to break priority ties. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.build_daily_plan()` | Filters by pet or completion status. The daily plan considers pending tasks due today or earlier and skips tasks that exceed the remaining time budget. |
| Conflict handling | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()`, `Scheduler.conflict_warning_for()` | Detects matching start times and due dates and provides warnings without blocking tasks. Does not detect duration overlaps. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Completing a daily or weekly task adds an uncompleted copy due 1 or 7 days after its original due date. One-time tasks do not repeat. |

## Testing PawPal+
## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Enter the owner's name, then add a pet (for example, Mochi which is a dog).
2. Add a task: "Morning walk" at 08:00, 30 minutes, high priority, assigned to Mochi.
3. Add a second task for Mochi also at 08:00, such as "Feed", low priority, and a warning appears saying two tasks overlap at 08:00. Both tasks are still saved.
4. Switch the Sort by option between Time and Priority, or filter to Pending tasks, to see the table reorder.
5. Set the available minutes and click Generate schedule. The plan appears as a table in time order, with a success banner showing the minutes used. Also, any pending tasks left out (over budget or not due yet) are listed in a warning.


**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
