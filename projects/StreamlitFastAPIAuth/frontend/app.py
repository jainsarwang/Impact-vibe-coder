
import streamlit as st
import requests

# --- Configuration ---
BACKEND_URL = "http://localhost:8000" # Replace with your backend URL if not running locally

# --- Streamlit App ---

st.set_page_config(page_title="Auth App", layout="centered")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'login' # 'login', 'signup', 'dashboard'

def switch_page(page_name):
    st.session_state['page'] = page_name
    st.rerun()

def login_form():
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            signup_button = st.form_submit_button("Go to Sign Up")

        if login_button:
            if username and password:
                try:
                    response = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.success("Login successful!")
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = response.json().get("username", username)
                        switch_page('dashboard')
                    else:
                        st.error(f"Login failed: {response.json().get('detail', 'Invalid credentials')}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Please ensure the backend is running.")
            else:
                st.warning("Please enter both username and password.")

        if signup_button:
             switch_page('signup')


def signup_form():
    st.subheader("Sign Up")
    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            signup_button = st.form_submit_button("Sign Up")
        with col2:
            login_button = st.form_submit_button("Go to Login")

        if signup_button:
            if username and password:
                try:
                    response = requests.post(f"{BACKEND_URL}/signup", json={"username": username, "password": password})
                    if response.status_code == 200:
                        st.success("Sign up successful! Please login.")
                        switch_page('login')
                    else:
                        st.error(f"Sign up failed: {response.json().get('detail', 'Username already registered')}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Please ensure the backend is running.")
            else:
                st.warning("Please enter both username and password.")

        if login_button:
            switch_page('login')

def dashboard():
    st.subheader(f"Welcome, {st.session_state['username']}!")
    st.write("This is your dashboard. You are logged in.")

    # Additional features can be added here
    st.write("---")
    st.write("Additional Features:")
    st.write("- Display user-specific content.")
    st.write("- Access protected resources from the backend.")
    st.write("- User profile settings (future feature).")

    if st.button("Logout"):
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        switch_page('login')

# --- Main App Logic ---
if st.session_state['authenticated']:
    dashboard()
else:
    if st.session_state['page'] == 'signup':
        signup_form()
    else: # default to login page
        login_form()

