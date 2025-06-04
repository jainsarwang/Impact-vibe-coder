import cv2
import mediapipe as mp
import numpy as np
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from GestureVolumeControl.utils import calculate_distance


def main():
    """Main function to initialize and run the volume control system."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)
    mp_drawing = mp.solutions.drawing_utils

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    while True:
        success, img = cap.read()
        if not success:
            print("Error: Could not read frame.")
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get the coordinates of the tip of the thumb and index finger
                thumb_tip = (int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * img.shape[1]),
                             int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * img.shape[0]))
                index_tip = (int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * img.shape[1]),
                             int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * img.shape[0]))

                # Calculate the distance between the thumb and index finger
                distance = calculate_distance(thumb_tip, index_tip)

                # Map the distance to a volume range (0 to 1)
                # Assuming a maximum distance of 200 pixels and a minimum of 20 pixels
                min_distance = 20
                max_distance = 200
                volume_level = np.interp(distance, [min_distance, max_distance], [0, 1])

                # Set the master volume
                volume.SetMasterVolumeLevelScalar(volume_level, None)

                # Draw landmarks and the line between thumb and index finger
                cv2.line(img, thumb_tip, index_tip, (255, 0, 0), 3)
                cv2.circle(img, thumb_tip, 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, index_tip, 10, (255, 0, 0), cv2.FILLED)
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Display the volume level
                cv2.putText(img, f'Volume: {int(volume_level * 100)}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Hand Gesture Volume Control", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
