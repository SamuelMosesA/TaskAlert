import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import threading
import base64
import os

BACKEND_URL = "http://127.0.0.1:8000" # Backend URL

# Function to fetch data from backend
def fetch_sections():
    response = requests.get(f"{BACKEND_URL}/sections/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching sections: {response.status_code}")
        return []

def fetch_tasks_by_section(section_id):
    response = requests.get(f"{BACKEND_URL}/sections/{section_id}/tasks")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching tasks: {response.status_code}")
        return []

def create_section(section_name):
    response = requests.post(f"{BACKEND_URL}/sections/", json={"name": section_name})
    return response

def create_task(section_id, summary, description, reminder_time):
    task_data = {
        "section_id": section_id,
        "summary": summary,
        "description": description,
        "reminder_time": reminder_time.isoformat()
    }
    response = requests.post(f"{BACKEND_URL}/tasks/", json=task_data)
    return response

def update_task_completion(task_id, is_completed):
    response = requests.put(f"{BACKEND_URL}/tasks/{task_id}", json={"is_completed": is_completed})
    return response

def update_task_reminder_time(task_id, reminder_time):
    response = requests.put(f"{BACKEND_URL}/tasks/{task_id}", json={"reminder_time": reminder_time.isoformat()})
    return response

def fetch_task(task_id):
    response = requests.get(f"{BACKEND_URL}/tasks/{task_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching task: {response.status_code}")
        return None

# Alerting Functionality
def play_audio(audio_file):
    try:
        with open(audio_file, 'rb') as f:
            data = f.read()
            b64_encoded = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay loop>
                <source src="data:audio/mp3;base64,{b64_encoded}" type="audio/mp3">
                Your browser does not support the audio element.
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
            time.sleep(5) # Play for 5 seconds (configurable)
            st.markdown('<audio autoplay loop><source src="" type="audio/mp3"></audio>', unsafe_allow_html=True) # Stop audio
    except Exception as e:
        st.error(f"Error playing audio: {e}")

def check_reminders(tasks_placeholder):
    while True:
        tasks = requests.get(f"{BACKEND_URL}/tasks/").json() # Fetch all tasks for reminder check. In prod, optimize this.
        now = datetime.now()
        for task in tasks:
            task_reminder_time = datetime.fromisoformat(task['reminder_time'])
            if task_reminder_time <= now and not task['is_completed']:
                with tasks_placeholder.container():
                    st.warning(f"Reminder! Task: {task['summary']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Complete", key=f"complete_{task['id']}"):
                            update_task_completion(task['id'], True)
                            st.success(f"Task '{task['summary']}' completed!")
                            # Rerender tasks (basic refresh, can be improved)
                            tasks_placeholder.empty() # Clear previous alerts
                            display_tasks_ui(tasks_placeholder)
                            break # Important to break to avoid duplicate buttons after state change.
                    with col2:
                        snooze_minutes = st.number_input("Snooze (minutes)", value=5, step=1, key=f"snooze_input_{task['id']}")
                        if st.button("Snooze", key=f"snooze_{task['id']}"):
                            new_reminder_time = now + timedelta(minutes=snooze_minutes)
                            update_task_reminder_time(task['id'], new_reminder_time)
                            st.info(f"Task '{task['summary']}' snoozed for {snooze_minutes} minutes.")
                            tasks_placeholder.empty() # Clear previous alerts
                            display_tasks_ui(tasks_placeholder)
                            break # Break to avoid duplicate buttons

                # Play audio alert in a separate thread to avoid blocking UI
                audio_thread = threading.Thread(target=play_audio, args=("alarm.mp3",)) # Replace with your audio file, ensure it's in the same directory or provide path.
                audio_thread.daemon = True # Allow main thread to exit even if audio thread is running
                audio_thread.start()
                time.sleep(1) # Check every 1 second (configurable - adjust for your needs)
                break # Check only one reminder at a time in this loop for simplicity - can be adjusted

def display_tasks_ui(tasks_placeholder):
    sections = fetch_sections()
    if not sections:
        st.info("No sections created yet. Please create a section to add tasks.")
        return

    with st.expander("Create New Task", expanded=False):
        with st.form("create_task_form"):
            section_options = {section['name']: section['id'] for section in sections}
            selected_section_name = st.selectbox("Section", options=list(section_options.keys()))
            selected_section_id = section_options[selected_section_name]
            task_summary = st.text_input("Task Summary")
            task_description = st.text_area("Description", value="")
            reminder_time = st.date_input("Reminder Date", value=datetime.now().date())
            reminder_time_time = st.time_input("Reminder Time", value=datetime.now().time())
            combined_reminder_time = datetime.combine(reminder_time, reminder_time_time)

            if st.form_submit_button("Add Task"):
                if task_summary:
                    response = create_task(selected_section_id, task_summary, task_description, combined_reminder_time)
                    if response.status_code == 200:
                        st.success("Task created successfully!")
                        tasks_placeholder.empty() # Clear and rerender tasks after adding a new task.
                        display_tasks_ui(tasks_placeholder)
                    else:
                        st.error(f"Error creating task: {response.status_code} - {response.text}")
                else:
                    st.error("Task summary is required.")

    for section in sections:
        tasks = fetch_tasks_by_section(section['id'])
        if tasks:
            with st.expander(f"Section: {section['name']} ({len(tasks)} tasks)", expanded=True):
                for task in tasks:
                    col1, col2 = st.columns([0.7, 0.3]) # Adjust column widths

                    with col1:
                        st.markdown(f"**{task['summary']}**")
                        if task['description']:
                            st.markdown(f"*{task['description']}*")
                        st.markdown(f"Reminder: {datetime.fromisoformat(task['reminder_time']).strftime('%Y-%m-%d %H:%M')}")

                    with col2:
                        is_complete_checkbox = st.checkbox("Completed", value=task['is_completed'], key=f"task_checkbox_{task['id']}")
                        if is_complete_checkbox != task['is_completed']: # Check if value changed
                            update_task_completion(task['id'], is_complete_checkbox)
                            st.rerun() # Basic refresh to update UI

def display_sections_ui():
    with st.expander("Manage Sections", expanded=False):
        with st.form("create_section_form"):
            section_name = st.text_input("Section Name")
            if st.form_submit_button("Add Section"):
                if section_name:
                    response = create_section(section_name)
                    if response.status_code == 200:
                        st.success("Section created successfully!")
                        st.rerun() # Refresh to show new section
                    else:
                        st.error(f"Error creating section: {response.status_code} - {response.text}")
                else:
                    st.error("Section name is required.")

def main():
    st.title("Task Alert App")

    display_sections_ui()

    tasks_placeholder = st.empty() # Placeholder to display tasks and alerts.
    display_tasks_ui(tasks_placeholder)

    # Reminder Check Thread (run in background)
    reminder_thread = threading.Thread(target=check_reminders, args=(tasks_placeholder,))
    reminder_thread.daemon = True # Allow main thread to exit
    reminder_thread.start()

if __name__ == "__main__":
    main()