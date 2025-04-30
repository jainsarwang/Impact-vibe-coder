import streamlit as st
import requests
import pandas as pd
from datetime import date

BACKEND_URL = 'http://localhost:8000'

# --- Functions to interact with the backend ---

def get_todos(completed: bool = None):
    url = f'{BACKEND_URL}/todos/'
    params = {}
    if completed is not None:
        params['completed'] = completed
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def create_todo(title: str, description: str = None, due_date: date = None, priority: str = None):
    url = f'{BACKEND_URL}/todos/'
    payload = {'title': title, 'description': description, 'due_date': str(due_date) if due_date else None, 'priority': priority}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def update_todo(todo_id: int, title: str = None, description: str = None, due_date: date = None, priority: str = None, completed: bool = None):
    url = f'{BACKEND_URL}/todos/{todo_id}'
    payload = {}
    if title: payload['title'] = title
    if description: payload['description'] = description
    if due_date: payload['due_date'] = str(due_date)
    if priority: payload['priority'] = priority
    if completed is not None: payload['completed'] = completed
    response = requests.patch(url, json=payload)
    response.raise_for_status()
    return response.json()

def delete_todo(todo_id: int):
    url = f'{BACKEND_URL}/todos/{todo_id}'
    response = requests.delete(url)
    response.raise_for_status()
    return response.json()

def filter_todos_by_priority(priority: str = None, due_date: date = None):
    url = f'{BACKEND_URL}/todos/filter/'
    params = {}
    if priority: params['priority'] = priority
    if due_date: params['due_date'] = str(due_date) if due_date else None
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# --- Streamlit App ---

st.title('To-Do List App')

# --- Create To-Do Item --- 
with st.expander('Add New To-Do'):
    new_todo_title = st.text_input('Title')
    new_todo_description = st.text_area('Description', value='')
    new_todo_due_date = st.date_input('Due Date', value=None)
    new_todo_priority = st.selectbox('Priority', options=[None, 'High', 'Medium', 'Low'], index=0)
    if st.button('Add To-Do'):
        if new_todo_title:
            create_todo(title=new_todo_title, description=new_todo_description, due_date=new_todo_due_date, priority=new_todo_priority)
            st.success('To-Do added!')
            st.experimental_rerun()
        else:
            st.error('Title is required.')

# --- Display To-Do Items --- 
todos = get_todos()
if todos:
    df = pd.DataFrame(todos)
    df['due_date'] = pd.to_datetime(df['due_date']).dt.date
    df = df.fillna('')
    st.dataframe(df, use_container_width=True)
else:
    st.info('No To-Do items yet.')

# --- Mark Complete/Delete --- 
with st.expander('Mark Complete/Delete To-Do'):
    todo_id_str = st.text_input('Enter To-Do ID:')
    if todo_id_str:
        try:
            todo_id = int(todo_id_str)
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Mark as Complete'):
                    update_todo(todo_id=todo_id, completed=True)
                    st.success(f'To-Do {todo_id} marked as complete!')
                    st.experimental_rerun()
            with col2:
                if st.button('Delete'):
                    delete_todo(todo_id=todo_id)
                    st.success(f'To-Do {todo_id} deleted!')
                    st.experimental_rerun()
        except ValueError:
            st.error('Invalid To-Do ID. Please enter a number.')

# --- Filter To-Dos --- 
with st.expander('Filter To-Dos'):
    filter_priority = st.selectbox('Filter by Priority', options=[None, 'High', 'Medium', 'Low'], index=0)
    filter_date = st.date_input('Filter by Due Date', value=None)
    if st.button('Apply Filters'):
        filtered_todos = filter_todos_by_priority(priority=filter_priority, due_date=filter_date)
        if filtered_todos:
            df_filtered = pd.DataFrame(filtered_todos)
            df_filtered['due_date'] = pd.to_datetime(df_filtered['due_date']).dt.date
            df_filtered = df_filtered.fillna('')
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.info('No To-Do items match the filter criteria.')

# --- Display Completed To-Dos --- 
if st.checkbox('Show Completed To-Dos'):
    completed_todos = get_todos(completed=True)
    if completed_todos:
        df_completed = pd.DataFrame(completed_todos)
        df_completed['due_date'] = pd.to_datetime(df_completed['due_date']).dt.date
        df_completed = df_completed.fillna('')
        st.dataframe(df_completed, use_container_width=True)
    else:
        st.info('No completed To-Do items.')
