# GestureVolumeControl

## Project Description

GestureVolumeControl is a Python-based system that allows users to control their computer's master volume using hand gestures. It leverages the MediaPipe library for hand landmark detection and the pycaw library for volume control. The system captures video frames using OpenCV, processes them with MediaPipe to identify hand landmarks, and then interprets specific hand gestures to adjust the volume accordingly.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd GestureVolumeControl
    ```

2.  **Install dependencies:**
    It is recommended to create a virtual environment before installing the dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate.bat  # On Windows
    ```
    Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Dependencies:**
    The project relies on the following libraries:
    *   opencv-python
    *   mediapipe
    *   pycaw
    *   numpy

## Usage Instructions

1.  **Run the main script:**
    ```bash
    python main.py
    ```

2.  **Gesture Recognition:**
    The system uses hand landmarks detected by MediaPipe to recognize gestures. Specific gestures are mapped to volume control actions (e.g., moving a finger up or down to increase or decrease volume).

3.  **Volume Control:**
    The pycaw library is used to set the master volume level based on the recognized hand gestures. The volume level is adjusted between 0.0 (mute) and 1.0 (maximum volume).

## System Overview

The GestureVolumeControl system works as follows:

1.  **Video Capture:** OpenCV captures video frames from the default camera.
2.  **Hand Landmark Detection:** MediaPipe's Hand module detects and tracks hands using 21 key points (landmarks).
3.  **Gesture Interpretation:** The system analyzes the position of the hand landmarks to recognize specific gestures.
4.  **Volume Adjustment:** Based on the recognized gesture, the system adjusts the master volume level using the pycaw library.
5.  **Visualization:** The system displays the video feed with the detected hand landmarks and volume level on the screen.
