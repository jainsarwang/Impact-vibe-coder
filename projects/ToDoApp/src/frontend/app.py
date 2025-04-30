
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"


def get_tasks():
    response = requests.get(f"{BACKEND_URL}/tasks/")
    return response.json()


def create_task(title, description):
    response = requests.post(
        f"{BACKEND_URL}/tasks/", json={"title": title, "description": description}
    )
    return response.json()


def update_task(task_id, status):
    response = requests.patch(f"{BACKEND_URL}/tasks/{task_id}", json={"status": status})
    return response.json()


def delete_task(task_id):
    response = requests.delete(f"{BACKEND_URL}/tasks/{task_id}")
    return response.json()


st.title("To-Do App")

# Input fields for adding tasks
new_task_title = st.text_input("Task Title")
new_task_description = st.text_area("Task Description")
if st.button("Add Task"):
    create_task(new_task_title, new_task_description)
    st.rerun()

# Display tasks
tasks = get_tasks()
for task in tasks:
    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
    with col1:
        st.write(task["title"])
        st.caption(task["description"])
    with col2:
        completed = st.checkbox("Complete", value=task["status"], key=f"complete_{task["id"]}")
        if completed != task["status"]:
            update_task(task["id"], completed)
            st.rerun()
    with col3:
        if st.button("Delete", key=f"delete_{task["id"]}"):  # Unique key for each button
            delete_task(task["id"])
            st.rerun()
