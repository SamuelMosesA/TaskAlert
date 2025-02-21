import streamlit as st
from streamlit_date_picker import date_picker, PickerType
from taskalert.backend import schemas
import requests
from datetime import datetime, date, time
from pydantic import ValidationError

API_REFRESH_COUNT_STATE = "api_refresh_count"
API_BASE = "http://localhost:8123"


@st.cache_data
def all_task_data_cache(refresh_count: int) -> list[schemas.Section]:
    st.write(refresh_count)
    response = requests.get("/".join([API_BASE, "sections"])) 
    assert response.ok
    return [schemas.Section.model_validate(section) for section in response.json()]

def get_all_data() -> list[schemas.Section]:
    refresh_count = st.session_state[API_REFRESH_COUNT_STATE]
    return all_task_data_cache(refresh_count=refresh_count)

def request_data_refresh()->None:
    st.session_state[API_REFRESH_COUNT_STATE] += 1


@st.dialog("Create Section")
def create_section()->None:
    section_name = st.text_input("Section Name")
    if st.button("Create", key="post_create_section"):
        payload = schemas.SectionCreate(name=section_name)
        response = requests.post("/".join([API_BASE, "sections"]), payload.model_dump_json())
        st.write(response)

def show_task_details(task: schemas.Task | None) -> schemas.TaskBase | None:
    default_summary = ""
    default_description = ""
    default_reminder = datetime.combine(date.today(), time(hour=12))
    default_completion = False
    if task is not None:
        default_summary = task.summary
        default_description = task.description
        default_reminder = task.reminder_time
        default_completion = task.is_completed

    summary = st.text_input(label="Task Summary", value=default_summary) 
    description = st.text_area(label="Task Description", value=default_description)
    reminder = date_picker(picker_type=PickerType.time, value=default_reminder)
    is_completed = st.checkbox(label="Is Completed", value=default_completion)
    try:
        return schemas.TaskBase(
            summary=summary,
            description=description,
            reminder_time=reminder,
            is_completed=is_completed
        )
    except ValidationError:
        return None

@st.dialog("Edit Task")
def edit_task(task: schemas.Task) -> None:
    task_details = show_task_details(task)
    if task_details is not None:
        payload = schemas.FullTaskUpdate(
            summary=task_details.summary,
            description=task_details.description,
            reminder_time=task_details.reminder_time,
            is_completed=task_details.is_completed
        )
        if st.button("Edit"):
            response = requests.put("/".join([API_BASE, "tasks", str(task.id)]), payload.model_dump_json())
            st.write(response)
            
@st.dialog("Create Task")
def create_task(section: schemas.Section) -> None:
    task_details = show_task_details(None)
    if task_details is not None:
        payload = schemas.TaskCreate(
            summary=task_details.summary,
            description=task_details.description,
            reminder_time=task_details.reminder_time,
            is_completed=task_details.is_completed,
            section_id=section.id
        )
        if st.button("Create"):
            response = requests.post("/".join([API_BASE, "tasks"]), payload.model_dump_json())
            st.write(response)

@st.fragment()
def display_subtaks(subtasks: list[schemas.Subtask], task_id: int)->None:
    for subtask in subtasks:
        button_col, text_col = st.columns([0.1, 0.9])
        with button_col:
            is_completed = st.checkbox(label="Completed", value=subtask.is_completed, key=f"task_checkbox_{subtask.id}")
        with text_col:
            st.text(subtask.step)
    button_col, text_col = st.columns([0.2, 0.8])
    with text_col:
        new_task = st.text_input("New Subtask", key=f"new_step_for_task_{task_id}")
    with button_col:
        if st.button("Add", use_container_width=True, key=f"add_subtask_for_task_{task_id}"):
            st.write(new_task)

        
@st.fragment()
def display_task(task:schemas.Task) -> None:
    with st.container(border=True):
        left_col, middle_col, right_col = st.columns([0.55, 0.35, 0.1])
        with left_col:
            task_summary = [task.summary]
            if task.is_completed:
                task_summary = ["✅"] + task_summary
            st.subheader(" ".join(task_summary))
            st.markdown(task.description)
            st.write(task.reminder_time)
        with right_col:
            if st.button("Edit Task", key=f"edit_task_{task.id}"):
                edit_task(task=task)
            if st.button("Delete Task", key=f"delete_task_{task.id}"):
                pass
        with middle_col:
            display_subtaks(subtasks=task.subtasks, task_id=task.id)

            
@st.fragment()
def display_section(section: schemas.Section) -> None:
    with st.expander(section.name, expanded=True):
        for task in section.tasks:
            display_task(task=task)
        left_col, right_col = st.columns(2)
        with right_col:
            if st.button(label="Delete Section", key=f"delete_section_{section.id}"):
                st.write("delete")
        with left_col:
            if st.button(label="Create Task", key=f"create_task_{section.id}"):
                create_task(section)


if not API_REFRESH_COUNT_STATE in st.session_state:
    st.session_state[API_REFRESH_COUNT_STATE] = 0

@st.fragment()
def display_ui()->None:
    if st.button("Refresh"):
        request_data_refresh()
        st.rerun(scope="fragment")
    if st.button("Create Section", key="create_section"):
        create_section()
    data = get_all_data()
    for section in data:
        display_section(section=section)

st.set_page_config(layout="wide", page_title="Task Alert")

st.title("Task Alert")

st.divider()

display_ui()