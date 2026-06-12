import os
import cv2
import time
from datetime import datetime
from pushbullet import Pushbullet  # Imports the Pushbullet library
from gesture_detector import GestureDetector 

# --- CONFIGURATION ---
# Your live access token is locked in right here:
API_KEY = "o.DSQiMuaxPHYIs74I75i4DnHIzlZzsAda" 

def send_phone_notification(timestamp):
    """Sends a push notification directly to your smartphone via Pushbullet."""
    try:
        pb = Pushbullet(API_KEY)
        title = "🚨 EMERGENCY: GestureGuard Alert!"
        body = f"An SOS gesture was detected and verified at {timestamp}. Please check the monitor."
        
        # This pushes the notification to your Android phone
        pb.push_note(title, body)
        print("📱 PUSH NOTIFICATION SENT SUCCESSFULLY TO YOUR PHONE!")
    except Exception as e:
        print(f"❌ Failed to send phone notification: {e}")

def log_alert():
    """Creates an 'alerts' folder if it doesn't exist and logs the incident."""
    folder_path = "alerts"
    file_path = os.path.join(folder_path, "alerts.log")
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print("📁 Created a brand-new 'alerts' folder!")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[ALERT] SOS Gesture Detected at: {current_time}\n"
    
    with open(file_path, "a") as log_file:
        log_file.write(log_line)
    
    print(f"✨ NEW LOG WRITTEN successfully to: {file_path} at {current_time}")
    
    # Trigger your Android phone notification immediately after logging
    send_phone_notification(current_time)

def main():
    cap = cv2.VideoCapture(0)
    detector = GestureDetector()

    print("GestureGuard Running... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)

        # 1. Process detection
        is_sos_triggered = detector.detect(frame)
        if is_sos_triggered:
            print("🚨 SOS ALERT TRIGGERED! 🚨")
            log_alert()  

        # 2. Draw the UI overlays
        frame = detector.draw_roi(frame)

        # 3. Display the frame
        cv2.imshow("GestureGuard - SOS Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()