import streamlit as st
import requests
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

# --- Authentication --- #

def signup():
    st.subheader("Create New Account")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")

    if st.button("Signup"):
        user_data = {"username": new_username, "password": new_password}
        response = requests.post(f"{BACKEND_URL}/users", json=user_data)
        if response.status_code == 201:
            st.success("Account created successfully! Please login.")
        else:
            st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")

def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        form_data = {"username": username, "password": password}
        response = requests.post(f"{BACKEND_URL}/token", data=form_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token
            st.session_state["username"] = username
            st.success("Logged in as {}".format(username))
            return True
        else:
            st.error("Login failed. Check username and password.")
            return False
    return None


def logout():
    if "token" in st.session_state:
        del st.session_state["token"]
        del st.session_state["username"]
        st.success("Logged out")
    else:
        st.warning("Not logged in")


# --- CRUD Operations for Items --- #

def create_item():
    st.subheader("Create New Task")
    title = st.text_input("Title")
    description = st.text_area("Description", max_chars=500)
    priority = st.selectbox("Priority", options=[1, 2, 3], index=2)  # 1: High, 2: Medium, 3: Low
    due_date_str = st.date_input("Due Date", value=None)
    due_date = datetime.combine(due_date_str, datetime.min.time()) if due_date_str else None

    if st.button("Create"): 
        if not title:
            st.error("Title is required")
            return

        item_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None,
        }
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(f"{BACKEND_URL}/items", json=item_data, headers=headers)
        if response.status_code == 201:
            st.success("Task created successfully!")
        else:
            st.error(f"Failed to create task: {response.json().get('detail', 'Unknown error')}")


def read_items():
    if "token" not in st.session_state:
        st.warning("Please log in to view your tasks.")
        return

    st.subheader("Your Tasks")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{BACKEND_URL}/items", headers=headers)
    if response.status_code == 200:
        items = response.json()
        if not items:
            st.info("No tasks yet. Create one!")
            return

        for item in items:
            st.write(f"**{item['title']}**")
            st.write(f"Description: {item['description']}")
            st.write(f"Priority: {item['priority']}")
            if item['due_date']:
                st.write(f"Due Date: {item['due_date']}")
            st.write(f"Completed: {item['completed']}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Edit {item['id']}", key=f"edit_{item['id']}"):
                    st.session_state['edit_item_id'] = item['id']
                    st.experimental_rerun()
            with col2:
                if st.button(f"Delete {item['id']}", key=f"delete_{item['id']}"):
                    delete_item(item['id'])
            with col3:
                if st.button(f"Mark Complete {item['id']}", key=f"complete_{item['id']}"):
                    update_item_completion(item['id'], True)

            st.markdown("---")

    else:
        st.error(f"Failed to fetch tasks: {response.json().get('detail', 'Unknown error')}")


def update_item_completion(item_id: int, completed: bool):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    item_data = {"completed": completed}
    response = requests.patch(f"{BACKEND_URL}/items/{item_id}", headers=headers, json=item_data)
    if response.status_code == 200:
        st.success("Task updated successfully!")
        st.experimental_rerun()
    else:
        st.error(f"Failed to update task: {response.json().get('detail', 'Unknown error')}")


def update_item(item_id: int):
    st.subheader("Edit Task")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{BACKEND_URL}/items/{item_id}", headers=headers)
    if response.status_code == 200:
        item = response.json()
        title = st.text_input("Title", value=item['title'])
        description = st.text_area("Description", value=item['description'], max_chars=500)
        priority = st.selectbox("Priority", options=[1, 2, 3], index=item['priority'] - 1)
        due_date_str = item['due_date']
        due_date = datetime.fromisoformat(due_date_str).date() if due_date_str else None
        due_date = st.date_input("Due Date", value=due_date)
        completed = st.checkbox("Completed", value=item['completed'])

        if st.button("Update Task"):
            item_data = {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": datetime.combine(due_date, datetime.min.time()).isoformat() if due_date else None,
                "completed": completed
            }
            response = requests.patch(f"{BACKEND_URL}/items/{item_id}", headers=headers, json=item_data)
            if response.status_code == 200:
                st.success("Task updated successfully!")
                del st.session_state['edit_item_id']
                st.experimental_rerun()
            else:
                st.error(f"Failed to update task: {response.json().get('detail', 'Unknown error')}")
    else:
        st.error(f"Failed to fetch task: {response.json().get('detail', 'Unknown error')}")


def delete_item(item_id: int):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.delete(f"{BACKEND_URL}/items/{item_id}", headers=headers)
    if response.status_code == 204:
        st.success("Task deleted successfully!")
        st.experimental_rerun()
    else:
        st.error(f"Failed to delete task: {response.json().get('detail', 'Unknown error')}")


# --- Main App --- #

def main():
    st.title("To-Do App")

    if "token" not in st.session_state:
        menu = ["Login", "Signup"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            if login():
                st.experimental_rerun()
        elif choice == "Signup":
            signup()
    else:
        st.sidebar.write(f"Welcome, {st.session_state['username']}!")
        st.sidebar.button("Logout", on_click=logout)

        menu = ["Tasks", "Create Task"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Tasks":
            if 'edit_item_id' in st.session_state:
                update_item(st.session_state['edit_item_id'])
            else:
                read_items()
        elif choice == "Create Task":
            create_item()

if __name__ == "__main__":
    main()
