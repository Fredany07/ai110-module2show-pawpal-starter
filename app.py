from datetime import time

import streamlit as st

# Step 1: Establish the connection — bring the logic layer into the UI.
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. .
"""
)

# Step 2: Manage the application "memory".
# Streamlit re-runs this script top-to-bottom on every interaction, so we keep
# a single Owner instance in st.session_state instead of rebuilding it each run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.divider()

# --- Owner settings -------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.set_availability(
    st.number_input(
        "Minutes available today",
        min_value=0,
        max_value=1440,
        value=owner.minutes_available or 60,
    )
)

st.divider()

# --- Step 3a: Adding a Pet ------------------------------------------------
st.subheader("Add a Pet")
col_a, col_b = st.columns(2)
with col_a:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col_b:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # The Owner class owns this responsibility, so the UI just delegates to it.
    owner.add_pet(Pet(name=new_pet_name, species=new_pet_species))
    st.success(f"Added {new_pet_name} ({new_pet_species}).")

if not owner.pets:
    st.info("No pets yet. Add one above to start scheduling tasks.")
    st.stop()

st.write("Current pets:")
st.table(
    [{"name": pet.name, "species": pet.species, "tasks": len(pet.tasks)} for pet in owner.pets]
)

st.divider()

# --- Step 3b: Scheduling a Task ------------------------------------------
st.subheader("Add a Task")
pet_labels = [f"{i}: {pet.name}" for i, pet in enumerate(owner.pets)]
selected_pet_label = st.selectbox("For which pet?", pet_labels)
selected_pet = owner.pets[int(selected_pet_label.split(":")[0])]

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    scheduled_time = st.time_input("Start time", value=time(8, 0))
with col5:
    recurring = st.selectbox("Repeats", ["none", "daily", "weekly"])

if st.button("Add task"):
    # Pet.add_task handles the data; the UI updates because Streamlit re-runs
    # and reads the now-updated object out of session_state.
    selected_pet.add_task(
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            scheduled_time=scheduled_time.strftime("%H:%M"),
            recurring=recurring,
        )
    )
    st.success(f"Added '{task_title}' to {selected_pet.name}.")

# --- Filter the task list by pet / status --------------------------------
st.write("All tasks:")
fcol1, fcol2 = st.columns(2)
with fcol1:
    pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
with fcol2:
    status_filter = st.selectbox("Filter by status", ["All", "pending", "completed"])

filtered = owner.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    status=None if status_filter == "All" else status_filter,
)
if filtered:
    st.table(
        [
            {
                "title": t.title,
                "time": t.scheduled_time or "—",
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "repeats": t.recurring,
                "done": "✅" if t.completed else "",
            }
            for t in filtered
        ]
    )
else:
    st.info("No tasks match the current filters.")

st.divider()

# --- Build the schedule ---------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler.from_owner(owner)
    plan = scheduler.build_plan()
    if plan:
        st.write("### Today's plan")
        st.table(
            [
                {
                    "#": i,
                    "time": t.scheduled_time or "—",
                    "title": t.title,
                    "priority": t.priority,
                    "duration_minutes": t.duration_minutes,
                }
                for i, t in enumerate(plan, start=1)
            ]
        )

    conflicts = scheduler.find_conflicts()
    if conflicts:
        for earlier, later in conflicts:
            st.warning(
                f"⚠️ '{earlier.title}' ({earlier.scheduled_time}) overlaps "
                f"'{later.title}' ({later.scheduled_time})."
            )

    st.text(scheduler.explain())
