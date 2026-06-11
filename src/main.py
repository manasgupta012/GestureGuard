print("run")
import cv2
from webcam import Webcam

def main():
    webcam = Webcam()

    while True:
        frame = webcam.read_frame()

        if frame is None:
            print("Failed to read frame")
            break

        cv2.imshow("GestureGuard", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    webcam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()