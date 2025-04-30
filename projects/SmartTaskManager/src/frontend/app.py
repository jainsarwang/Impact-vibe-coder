import streamlit as st
import requests
import datetime

BACKEND_URL = "http://localhost:8000"

# Function to fetch tasks from the backend
def get_tasks():
    try:
        response = requests.get(f"{BACKEND_URL}/tasks/")
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks: {e}")
        return []

# Function to create a new task
def create_task(task_data):
    try:
        response = requests.post(f"{BACKEND_URL}/tasks/", json=task_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating task: {e}")
        return None

# Function to update a task
def update_task(task_id, task_data):
    try:
        response = requests.put(f"{BACKEND_URL}/tasks/{task_id}", json=task_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating task: {e}")
        return None

# Function to delete a task
def delete_task(task_id):
    try:
        response = requests.delete(f"{BACKEND_URL}/tasks/{task_id}")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting task: {e}")
        return False

# Main Streamlit app
def main():
    st.title("Smart Task Manager")

    # Load tasks
    tasks = get_tasks()

    # Add new task form
    with st.expander("Add New Task"):
        with st.form("add_task"):
            title = st.text_input("Title")
            description = st.text_area("Description")
            due_date = st.date_input("Due Date", value=datetime.date.today())
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            tags = st.text_input("Tags (comma-separated)")
            submitted = st.form_submit_button("Add Task")

            if submitted:
                task_data = {
                    "title": title,
                    "description": description,
                    "due_date": str(due_date),
                    "priority": priority,
                    "tags": tags
                }
                new_task = create_task(task_data)
                if new_task:
                    st.success("Task added successfully!")
                    # Refresh tasks after adding
                    tasks = get_tasks()

    # Display tasks
    if tasks:
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.subheader(task["title"])
                    st.write(task["description"])
                    st.write(f"Due Date: {task["due_date"]}")
                    st.write(f"Priority: {task["priority"]}")
                    st.write(f"Tags: {task["tags"]}")

                with col2:
                    if st.button("Mark Complete", key=f"complete_{task['id']}"):
                        updated_task = update_task(task["id"], {"status": True})
                        if updated_task:
                            st.success("Task marked as complete!")
                            tasks = get_tasks()

                    if st.button("Delete", key=f"delete_{task['id']}"):
                        if delete_task(task["id"]):
                            st.success("Task deleted!")
                            tasks = get_tasks()

                with col3:
                    if st.button("Edit", key=f"edit_{task['id']}"):
                        # Implement edit functionality here (e.g., open a modal)
                        st.write("Edit functionality not implemented yet.")

    else:
        st.info("No tasks yet. Add some!")

if __name__ == "__main__":
    main()
