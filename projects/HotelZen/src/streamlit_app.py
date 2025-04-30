import streamlit as st
import requests
import json
import os
import zipfile
import io

BACKEND_URL = "http://127.0.0.1:5000"

# Custom CSS for styling
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #262730;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #31333f;
    }
    .stButton>button {
        color: #4F8BF9;
        border-color: #4F8BF9;
    }
    .stTextInput>label {
        color: #31333f;
    }
    .stNumberInput>label {
        color: #31333f;
    }
    .stSelectbox>label {
        color: #31333f;
    }
    .stJson {
        background-color: #f0f2f6;
        border: 1px solid #ced4da;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to display project directory in sidebar
def display_project_directory():
    st.sidebar.header("Project Directory")
    project_dir = "HotelZen"
    files = []
    for root, _, filenames in os.walk(project_dir):
        for filename in filenames:
            files.append(os.path.join(root, filename).replace("\\", "\\"))

    for file in files:
        st.sidebar.text(file)

# Function to create a zip file in memory
def zip_files(directory):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))
    memory_file.seek(0)
    return memory_file

# Main Streamlit app
def main():
    st.title("HotelZen Management")

    # Sidebar for navigation
    menu = ["Registration", "Login", "Hotels", "Rooms", "Bookings", "Payment", "Download Project"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Registration":
        st.header("User Registration")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"): 
            data = {"username": username, "password": password}
            response = requests.post(f"{BACKEND_URL}/register", json=data)
            if response.status_code == 201:
                st.success(response.json()["message"])
            else:
                st.error(response.json()["message"])

    elif choice == "Login":
        st.header("User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"): 
            data = {"username": username, "password": password}
            response = requests.post(f"{BACKEND_URL}/login", json=data)
            if response.status_code == 200:
                st.success(response.json()["message"])
                st.session_state.user = response.json()["user"]
            else:
                st.error(response.json()["message"])

    elif choice == "Hotels":
        st.header("Hotel List")
        response = requests.get(f"{BACKEND_URL}/hotels")
        if response.status_code == 200:
            hotels = response.json()
            st.json(hotels)
        else:
            st.error("Failed to fetch hotels")

    elif choice == "Rooms":
        st.header("Room List")
        response = requests.get(f"{BACKEND_URL}/rooms")
        if response.status_code == 200:
            rooms = response.json()
            st.json(rooms)
        else:
            st.error("Failed to fetch rooms")

    elif choice == "Bookings":
        st.header("Bookings Management")
        if 'user' in st.session_state:
            response = requests.get(f"{BACKEND_URL}/bookings")
            if response.status_code == 200:
                bookings = response.json()
                st.json(bookings)

                # Booking Creation
                st.subheader("Create New Booking")
                room_id = st.number_input("Room ID", min_value=1, step=1)
                check_in_date = st.date_input("Check-in Date")
                check_out_date = st.date_input("Check-out Date")

                if st.button("Create Booking"):
                    data = {
                        "user_id": st.session_state.user['user']['id'],
                        "room_id": room_id,
                        "check_in_date": str(check_in_date),
                        "check_out_date": str(check_out_date),
                    }
                    response = requests.post(f"{BACKEND_URL}/bookings", json=data)
                    if response.status_code == 201:
                        st.success(response.json()["message"])
                    else:
                        st.error(response.json()["message"])

            else:
                st.error("Failed to fetch bookings")
        else:
            st.warning("Please login to view and manage bookings.")

    elif choice == "Payment":
        st.header("Payment Processing")
        if 'user' in st.session_state:
            booking_id = st.number_input("Booking ID", min_value=1, step=1)
            amount = st.number_input("Amount", min_value=1.0)

            if st.button("Process Payment"):
                data = {"booking_id": booking_id, "amount": amount}
                response = requests.post(f"{BACKEND_URL}/payment", json=data)
                if response.status_code == 200:
                    st.success(response.json()["message"])
                else:
                    st.error(response.json()["message"])
        else:
            st.warning("Please login to process payments.")

    elif choice == "Download Project":
        st.header("Download Project")
        zip_buffer = zip_files("HotelZen")
        st.download_button(
            label="Download HotelZen Project",
            data=zip_buffer,
            file_name="HotelZen.zip",
            mime="application/zip",
        )

    # Display project directory in the sidebar
    display_project_directory()

if __name__ == "__main__":
    main()
