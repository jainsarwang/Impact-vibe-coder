# HotelZen User Manual

## Introduction

HotelZen is a hotel management application built with Flask and Streamlit. It allows users to manage hotels, rooms, bookings, and process payments.

## Setup

1.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables:**
    Create a `.env` file in the `HotelZen` directory and add the following:

    ```
    SECRET_KEY=your_secret_key
    ```

## Running the Application

1.  **Run the Flask backend:**

    ```bash
    python src\app.py
    ```

2.  **Run the Streamlit frontend:**

    ```bash
    streamlit run src\streamlit_app.py
    ```

## Features

*   **Registration:** Allows new users to register.
*   **Login:** Allows registered users to log in.
*   **Hotels:** Displays a list of hotels.
*   **Rooms:** Displays a list of rooms.
*   **Bookings:** Allows users to create, view, update, and delete bookings.
*   **Payment:** Allows users to process payments for bookings.

## Usage

1.  **Registration:**
    *   Navigate to the "Registration" page.
    *   Enter a username and password.
    *   Click the "Register" button.

2.  **Login:**
    *   Navigate to the "Login" page.
    *   Enter your username and password.
    *   Click the "Login" button.

3.  **Hotels:**
    *   Navigate to the "Hotels" page to view a list of hotels.

4.  **Rooms:**
    *   Navigate to the "Rooms" page to view a list of rooms.

5.  **Bookings:**
    *   Navigate to the "Bookings" page.
    *   Create a new booking by entering the room ID, check-in date, and check-out date.
    *   View existing bookings.
    *   Update or delete bookings as needed.

6.  **Payment:**
    *   Navigate to the "Payment" page.
    *   Enter the booking ID and amount.
    *   Click the "Process Payment" button.

## Project Directory

The project directory structure is as follows:

```
HotelZen/
├── data/
│   ├── hotels.json
│   ├── rooms.json
│   ├── users.json
│   └── bookings.json
├── src/
│   ├── app.py
│   └── streamlit_app.py
├── static/
├── templates/
├── package.json
├── requirements.txt
└── User_Manual.md
```
