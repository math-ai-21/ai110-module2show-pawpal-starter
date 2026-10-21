from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", "08:00"))

    assert len(pet.tasks) == 1


def test_daily_task_creates_next_day_occurrence():
    from datetime import date, timedelta
    owner = Owner("Jo")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Walk", "08:00", "daily")
    pet.add_task(task)

    nxt = Scheduler(owner).complete_task(task)

    assert task.completed
    assert nxt is not None and not nxt.completed
    assert nxt.due_date == date.today() + timedelta(days=1)
    assert nxt.pet_name == "Mochi" and nxt in pet.tasks


def test_weekly_task_creates_next_week_occurrence():
    from datetime import date, timedelta
    owner = Owner("Jo")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Groom", "15:00", "weekly")
    pet.add_task(task)

    nxt = Scheduler(owner).complete_task(task)

    assert nxt.due_date == date.today() + timedelta(days=7)


def test_one_off_task_has_no_next_occurrence():
    owner = Owner("Jo")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Vet", "10:00", "once")
    pet.add_task(task)

    assert Scheduler(owner).complete_task(task) is None
    assert len(pet.tasks) == 1


def test_future_occurrence_not_in_todays_plan():
    owner = Owner("Jo")
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    task = Task("Walk", "08:00", "daily")
    pet.add_task(task)
    sched = Scheduler(owner)
    sched.complete_task(task)

    assert sched.build_daily_plan() == []


def _two_pets():
    owner = Owner("Jo")
    mochi, rex = Pet("Mochi", "dog"), Pet("Rex", "cat")
    owner.add_pet(mochi)
    owner.add_pet(rex)
    return owner, mochi, rex


def test_conflict_same_pet_same_time():
    owner, mochi, _ = _two_pets()
    mochi.add_task(Task("Walk", "08:00"))
    mochi.add_task(Task("Feed", "08:00"))
    s = Scheduler(owner)
    assert len(s.find_conflicts(same_pet=True)) == 1
    assert s.find_conflicts(same_pet=False) == []
    assert "same pet" in s.conflict_warnings()[0]


def test_conflict_different_pets_same_time():
    owner, mochi, rex = _two_pets()
    mochi.add_task(Task("Walk", "08:00"))
    rex.add_task(Task("Feed", "08:00"))
    s = Scheduler(owner)
    assert len(s.find_conflicts(same_pet=False)) == 1
    assert "different pets" in s.conflict_warnings()[0]


def test_no_conflict_for_different_times_or_days():
    from datetime import date, timedelta
    owner, mochi, rex = _two_pets()
    mochi.add_task(Task("Walk", "08:00"))
    rex.add_task(Task("Feed", "09:00"))
    rex.add_task(Task("Play", "08:00", due_date=date.today() + timedelta(days=1)))
    assert Scheduler(owner).find_conflicts() == []


def test_conflict_warning_for_returns_message_not_exception():
    owner, mochi, rex = _two_pets()
    mochi.add_task(Task("Walk", "08:00"))
    new = Task("Feed", "08:00")
    rex.add_task(new)
    msg = Scheduler(owner).conflict_warning_for(new)
    assert msg is not None and "Walk" in msg and "08:00" in msg
    assert new in rex.tasks  # still added


def test_conflict_warning_for_none_when_clear():
    owner, mochi, _ = _two_pets()
    t = Task("Walk", "08:00")
    mochi.add_task(t)
    assert Scheduler(owner).conflict_warning_for(t) is None
