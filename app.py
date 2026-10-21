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
        new_task = Task(
            description=task_title,
            time=task_time.strftime("%H:%M"),
            duration_minutes=int(duration),
            priority=priority,
        )
        target.add_task(new_task)
        warning = Scheduler(owner).conflict_warning_for(new_task)
        if warning:
            st.warning(warning)  # task is still saved; user just gets a heads-up

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": t.pet_name,
                "task": t.description,
                "time": t.time,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add a pet, then add a task.")

st.divider()

st.subheader("Build Schedule")
st.caption("Picks pending tasks by priority within the owner's available time.")

owner.available_minutes = int(
    st.number_input("Available minutes today", min_value=1, max_value=1440,
                    value=owner.available_minutes)
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan_lines = scheduler.explain_plan()
    if not plan_lines:
        st.info("Nothing to schedule. Add a pet and some pending tasks first.")
    else:
        st.success("Today's plan")
        for line in plan_lines:
            st.write("- " + line)
        for warning in scheduler.conflict_warnings():
            st.warning(warning)
