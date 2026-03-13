from ultralytics import YOLO
import cv2
import os
import numpy as np
from datetime import datetime
from playsound import playsound
import face_recognition
from email_alert import send_email_alert


os.makedirs("captures", exist_ok=True)
os.makedirs("known_faces", exist_ok=True)

model = YOLO("yolov8n.pt")

known_face_encodings = []
known_face_names = []

for file_name in os.listdir("known_faces"):
    if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join("known_faces", file_name)

        try:
            # Load with OpenCV, then convert to RGB uint8
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not read {file_name}")
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = np.ascontiguousarray(image, dtype=np.uint8)

            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(file_name)[0])
                print(f"Loaded known face: {file_name}")
            else:
                print(f"No face found in: {file_name}")

        except Exception as e:
            print(f"Could not load {file_name}: {e}")

camera = cv2.VideoCapture(0)
last_saved_time = 0

while True:
    ret, frame = camera.read()

    if not ret:
        print("Camera error")
        break

    results = model(frame)

    annotated_frame = frame.copy()
    person_found = False

    for r in results:
        annotated_frame = r.plot()

        for box in r.boxes:
            if int(box.cls[0]) == 0:
                person_found = True

    # Convert webcam frame to exact format required by face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    detected_name = "Unknown"

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_face_names[match_index]

        detected_name = name

        cv2.rectangle(annotated_frame, (left, top), (right, bottom), (255, 0, 0), 2)
        cv2.putText(
            annotated_frame,
            name,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2
        )

    if person_found:
        current_time = datetime.now().timestamp()

        if current_time - last_saved_time > 5:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"intruder_{timestamp}.jpg"
            filepath = f"captures/{image_name}"

            cv2.imwrite(filepath, annotated_frame)

            with open("events.txt", "a") as f:
                f.write(f"{timestamp} : Person detected : {detected_name} : {image_name}\n")

            if detected_name == "Unknown":
                playsound("alarm.wav")
                send_email_alert(filepath)
                print("Unknown person detected! Alarm triggered and email sent.")
            else:
                print(f"Known person detected: {detected_name}")

            last_saved_time = current_time

    cv2.imshow("Smart AI Security", annotated_frame)

    if cv2.waitKey(1) == 27:
        break

camera.release()
cv2.destroyAllWindows()
