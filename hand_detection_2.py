# Importing Libraries
import cv2
import mediapipe as mp
from flask import Flask, render_template, Response
from flask_socketio import SocketIO

# Used to convert protobuf message to a dictionary.
from google.protobuf.json_format import MessageToDict

app = Flask(__name__)
socketio = SocketIO(app)

# Initializing the Model
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2)

# Start capturing video from webcam
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # Read video frame by frame
        success, img = cap.read()

        # Flip the image(frame)
        img = cv2.flip(img, 1)

        # Convert BGR image to RGB image
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the RGB image
        results = hands.process(imgRGB)

        hands_on = ""
        # If hands are present in image(frame)
        if results.multi_hand_landmarks:
            # hands_on = ""
            # Both Hands are present in image(frame)
            if len(results.multi_handedness) == 2:
                # Display 'Both Hands' on the image
                # cv2.putText(img, 'Both Hands', (250, 50),
                #             cv2.FONT_HERSHEY_COMPLEX,
                #             0.9, (0, 255, 0), 2)
                hands_on = 'Both Hands'

            # If any hand present
            else:
                for i in results.multi_handedness:

                    # Return whether it is Right or Left Hand
                    label = MessageToDict(i)['classification'][0]['label']

                    if label == 'Left':
                        # Display 'Left Hand' on
                        # left side of window
                        # cv2.putText(img, label + ' Hand',
                        #             (20, 50),
                        #             cv2.FONT_HERSHEY_COMPLEX,
                        #             0.9, (0, 255, 0), 2)
                        hands_on = 'Left Hand'

                    if label == 'Right':
                        # Display 'Left Hand'
                        # on left side of window
                        # cv2.putText(img, label + ' Hand', (460, 50),
                        #             cv2.FONT_HERSHEY_COMPLEX,
                        #             0.9, (0, 255, 0), 2)
                        hands_on = 'Right Hand'

        # Display Video and when 'q'
        # is entered, destroy the window
        # _, buffer2 = cv2.imencode('.jpg', img)
        # frame_bytes2 = buffer2.tobytes()
        #
        # socketio.emit('update_type', {"HandOn": hands_on})
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes2 + b'\r\n')

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed1')
def video_feed1():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
