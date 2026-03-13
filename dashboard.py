from flask import Flask, Response, render_template_string, send_from_directory, request, redirect, url_for
import cv2
import os
from ultralytics import YOLO
import face_recognition
import numpy as np
from email_alert import send_email_alert
from playsound import playsound
from datetime import datetime


app = Flask(__name__)

model = YOLO("yolov8n.pt")

os.makedirs("captures", exist_ok=True)
os.makedirs("known_faces", exist_ok=True)

known_face_encodings = []
known_face_names = []

for file_name in os.listdir("known_faces"):
    if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join("known_faces", file_name)
        image = cv2.imread(image_path)

        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = np.ascontiguousarray(image, dtype=np.uint8)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(os.path.splitext(file_name)[0])

camera = cv2.VideoCapture(0)
last_status = "Monitoring"
last_saved_time = 0

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Security Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: white;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 95%;
            margin: 20px auto;
        }
        h1 {
            text-align: center;
            color: #38bdf8;
            margin-bottom: 20px;
        }
        .status-bar {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            padding: 14px;
            border-radius: 12px;
            margin-bottom: 20px;
            background: {{ status_color }};
        }
        .grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }
        .card {
            background: #1e293b;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        }
        .card h3 {
            margin-top: 0;
            color: #38bdf8;
        }
        .video-feed {
            width: 100%;
            border-radius: 10px;
            border: 2px solid #334155;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.5;
        }
        .gallery {
            margin-top: 20px;
        }
        .gallery-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 10px;
        }
        .gallery-item {
            background: #1e293b;
            padding: 12px;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .gallery-item img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .gallery-item p {
            font-size: 13px;
            color: #cbd5e1;
            margin: 10px 0;
            text-align: center;
            word-break: break-word;
        }
        .actions {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .btn {
            text-decoration: none;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
            color: white;
        }
        .btn-download {
            background: #2563eb;
        }
        .btn-delete {
            background: #dc2626;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 20px;
        }
        .info-box {
            background: #1e293b;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        .info-box .label {
            color: #94a3b8;
            font-size: 14px;
        }
        .info-box .value {
            font-size: 22px;
            font-weight: bold;
            margin-top: 8px;
            color: #f8fafc;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Smart Security Dashboard</h1>

        <div class="status-bar">
            Current Status: {{ status }}
        </div>

        <div class="info-grid">
            <div class="info-box">
                <div class="label">System</div>
                <div class="value">Running</div>
            </div>
            <div class="info-box">
                <div class="label">Evidence Images</div>
                <div class="value">{{ image_count }}</div>
            </div>
            <div class="info-box">
                <div class="label">Recent Events</div>
                <div class="value">{{ event_count }}</div>
            </div>
            <div class="info-box">
                <div class="label">Email Alerts</div>
                <div class="value">{{ email_status }}</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Live Camera Feed</h3>
                <img class="video-feed" src="/video_feed">
            </div>

            <div class="card">
                <h3>Recent Events</h3>
                <pre>{{ events }}</pre>
            </div>
        </div>

        <div class="gallery">
            <div class="card">
                <h3>Captured Evidence</h3>
                <div class="gallery-grid">
                    {% for image in images %}
                    <div class="gallery-item">
                        <img src="/captures/{{ image }}" alt="{{ image }}">
                        <p>{{ image }}</p>
                        <div class="actions">
                            <a class="btn btn-download" href="/download/{{ image }}">Download</a>
                            <form method="POST" action="/delete/{{ image }}" style="display:inline;">
                                <button class="btn btn-delete" type="submit">Delete</button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                {% if not images %}
                <p>No evidence images found yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

def generate_frames():
    global last_status, last_saved_time

    while True:
        success, frame = camera.read()
        if not success:
            break

        results = model(frame)
        annotated_frame = frame.copy()
        detected_name = "Unknown"
        person_found = False

        for r in results:
            annotated_frame = r.plot()

            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    person_found = True

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

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

            if detected_name == "Unknown":
                last_status = "⚠ Unknown Person Detected"

                # Send alert only once every 15 seconds
                if current_time - last_saved_time > 15:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_name = f"intruder_{timestamp}.jpg"
                    filepath = os.path.join("captures", image_name)

                    cv2.imwrite(filepath, annotated_frame)

                    with open("events.txt", "a") as f:
                        f.write(f"{timestamp} : Person detected : Unknown : {image_name}\n")

                    playsound("alarm.wav")
                    send_email_alert(filepath)

                    print("Unknown person detected! Alarm triggered and email sent.")
                    last_saved_time = current_time

            else:
                last_status = f"Known Person: {detected_name}"

        else:
            last_status = "Monitoring"

        ret, buffer = cv2.imencode(".jpg", annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/")
def index():
    global last_status

    if os.path.exists("events.txt"):
        with open("events.txt", "r") as f:
            lines = f.readlines()
            events = "".join(lines[-10:])
            event_count = len(lines)
    else:
        events = "No events yet."
        event_count = 0

    images = []
    if os.path.exists("captures"):
        images = sorted(os.listdir("captures"), reverse=True)[:12]

    image_count = len(os.listdir("captures")) if os.path.exists("captures") else 0

    status_color = "#16a34a"
    if "Unknown" in last_status:
        status_color = "#dc2626"
    elif "Known Person" in last_status:
        status_color = "#2563eb"

    if os.path.exists("email_status.txt"):
        with open("email_status.txt", "r") as f:
            email_status = f.read().strip()
            if not email_status:
                email_status = "enabled"
    else:
        email_status = "enabled"
    return render_template_string(
        HTML,
        events=events,
        images=images,
        status=last_status,
        status_color=status_color,
        image_count=image_count,
        event_count=event_count,
        email_status=email_status
    )

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/captures/<path:filename>")
def captures(filename):
    return send_from_directory("captures", filename)

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory("captures", filename, as_attachment=True)

@app.route("/delete/<path:filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join("captures", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
