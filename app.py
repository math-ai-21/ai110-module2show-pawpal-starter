import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet")

# st.session_state works like a dictionary that survives Streamlit reruns.
# Only create the Owner if the "owner" key isn't in the vault yet.
if "owner" not in st.session_state:
    st.session_state["owner"] = Owner(name="Jordan")
owner = st.session_state["owner"]  # same object on every rerun

owner.name = st.text_input("Owner name", value=owner.name)

col_a, col_b = st.columns(2)
with col_a:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_b:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if any(p.name == pet_name for p in owner.pets):
        st.warning(f"{pet_name} is already added.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Tasks are stored on the pet inside the persisted Owner.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.time_input("Time")
with col3:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if owner.pets:
    target_name = st.selectbox("Assign to", [p.name for p in owner.pets])
    if st.button("Add task"):
        target = next(p for p in owner.pets if p.name == target_name)
        time_str = task_time.strftime("%H:%M")
        is_duplicate = any(
            t.description == task_title and t.time == time_str and not t.completed
            for t in target.tasks
        )
        if is_duplicate:
            st.warning(f"{target_name} already has '{task_title}' at {time_str}. Not added again.")
        else:
            new_task = Task(
                description=task_title,
                time=time_str,
                duration_minutes=int(duration),
                priority=priority,
            )
            target.add_task(new_task)
            st.success(f"Added '{task_title}' for {target_name} at {time_str}.")

scheduler = Scheduler(owner)
all_tasks = scheduler.get_all_tasks()


def tasks_to_rows(tasks):
    """Convert Task objects into display rows for st.table."""
    return [
        {
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority.capitalize(),
            "Status": "Done" if t.completed else "Pending",
        }
        for t in tasks
    ]


def show_conflicts(scheduler):
    """One warning per clashing time slot, instead of one per pair of tasks."""
    slots = {}
    for a, b in scheduler.find_conflicts():
        slot = slots.setdefault((a.due_date, a.time), [])
        for t in (a, b):
            if not any(t is s for s in slot):
                slot.append(t)
    if not slots:
        st.success("No scheduling conflicts.")
        return
    for (due, time), tasks in sorted(slots.items()):
        names = ", ".join(f"{t.pet_name}: {t.description}" for t in tasks)
        st.warning(f"{len(tasks)} tasks overlap at {time} on {due} - {names}")


st.markdown("### Your tasks")
if not all_tasks:
    st.info("No tasks yet. Add a pet, then add a task.")
else:
    show_conflicts(scheduler)

    col_s, col_f, col_p = st.columns(3)
    with col_s:
        sort_choice = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
    with col_f:
        status_choice = st.selectbox("Status", ["All", "Pending", "Completed"])
    with col_p:
        pet_choice = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])

    filtered = scheduler.filter_tasks(
        completed={"All": None, "Pending": False, "Completed": True}[status_choice],
        pet_name=None if pet_choice == "All" else pet_choice,
    )
    ordered = (
        scheduler.sort_by_time(filtered)
        if sort_choice == "Time"
        else scheduler.sort_by_priority(filtered)
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Showing", f"{len(ordered)} of {len(all_tasks)}")
    m2.metric("Pending", len(scheduler.filter_tasks(completed=False)))
    m3.metric("Completed", len(scheduler.filter_tasks(completed=True)))

    if ordered:
        st.table(tasks_to_rows(ordered))
    else:
        st.info("No tasks match the current filters.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks pending tasks by priority within the owner's available time.")

owner.available_minutes = int(
    st.number_input("Available minutes today", min_value=1, max_value=1440,
                    value=owner.available_minutes)
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan()
    if not plan:
        st.info("Nothing to schedule. Add a pet and some pending tasks first.")
    else:
        used = sum(t.duration_minutes for t in plan)
        st.success(
            f"Today's plan: {len(plan)} task(s), {used} of "
            f"{owner.available_minutes} minutes used."
        )
        st.table(tasks_to_rows(plan))  # already sorted by time
        skipped = [
            t for t in scheduler.sort_by_priority(scheduler.filter_tasks(completed=False))
            if t not in plan
        ]
        if skipped:
            st.warning(
                "Not scheduled (over the time budget or not due yet): "
                + ", ".join(f"{t.pet_name}'s {t.description}" for t in skipped)
            )
