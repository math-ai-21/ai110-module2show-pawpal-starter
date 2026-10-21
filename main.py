from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Sam", available_minutes=90)

    biscuit = Pet("Biscuit", "dog", age=4)
    mia = Pet("Mia", "cat", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mia)

    biscuit.add_task(Task("Morning walk", "08:00", "daily", duration_minutes=30, priority="high"))
    biscuit.add_task(Task("Evening walk", "18:00", "daily", duration_minutes=30, priority="medium"))
    mia.add_task(Task("Breakfast", "08:30", "daily", duration_minutes=10, priority="high"))
    mia.add_task(Task("Give medication", "12:00", "daily", duration_minutes=5, priority="high"))
    mia.add_task(Task("Grooming", "15:00", "weekly", duration_minutes=20, priority="low"))

    scheduler = Scheduler(owner)

    print(f"Today's Schedule for {owner.name} ({owner.available_minutes} min available)")
    print("=" * 60)
    for line in scheduler.explain_plan():
        print(line)

    conflicts = scheduler.find_conflicts()
    if conflicts:
        print("\nConflicts:")
        for a, b in conflicts:
            print(f"  {a.time}: {a.pet_name} {a.description} vs {b.pet_name} {b.description}")


if __name__ == "__main__":
    main()
