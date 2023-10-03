import cv2  # computer vision
import mediapipe as mp  # the actual hand detection and tracking on our input image
from flask import Flask, render_template, Response
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
video_path = r"C:\project\python\Python sample videos\Side view\VID_20231003_110032.mp4"
cap = cv2.VideoCapture(video_path)

# Pre-trained models and functions for detecting and tracking hands in images and videos.
mpHands = mp.solutions.hands

# Detect and track hands in each frame of the video stream.
hands = mpHands.Hands()

# Utility functions for drawing landmarks and connections on images
# Visualize the detected hand landmarks and connections.
mpDraw = mp.solutions.drawing_utils

def generate_frames():
    while True:
        success, image = cap.read()
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        drawing_occurred = False
        if results.multi_hand_landmarks:
            for handLMS in results.multi_hand_landmarks:
                for id, lm in enumerate(handLMS.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    if id == 20:
                        cv2.circle(image, (cx, cy), 25, (255, 0, 255), cv2.FILLED)
                        drawing_occurred = True
                # mpDraw.draw_landmarks(image, handLMS, mpHands.HAND_CONNECTIONS)

        _, buffer2 = cv2.imencode('.jpg', image)
        frame_bytes2 = buffer2.tobytes()

        if drawing_occurred:
            socketio.emit('update_type', {"height": True})
        else:
            socketio.emit('update_type', {"height": False})
        key = cv2.waitKey(30)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes2 + b'\r\n')
        if key == 27:
            break
        elif key == ord("q"):
            break
        # cap.release()
        # cv2.destroyAllWindows()
        # cv2.imshow("Image", image)
        # cv2.waitKey(1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
