\# AI Smart Security Monitoring System



An AI-powered home security system built with \*\*Python, YOLOv8, OpenCV, Face Recognition, Flask, and Email Alerts\*\*.



This system detects people in real time, identifies known vs unknown individuals, captures evidence, triggers alarms, sends email notifications, and provides a live dashboard for remote monitoring.



\---



\## Features



\- Real-time \*\*person detection\*\* using YOLOv8

\- \*\*Face recognition\*\* for known and unknown people

\- \*\*Intruder detection\*\* with automatic image capture

\- \*\*Alarm trigger\*\* for unknown persons

\- \*\*Email alerts\*\* with captured evidence

\- \*\*Event logging\*\* in a local log file

\- \*\*Live dashboard\*\* using Flask

\- \*\*Remote monitoring\*\* using ngrok



\---



\## Tech Stack



\- Python

\- OpenCV

\- YOLOv8

\- face\_recognition / dlib

\- Flask

\- SMTP Email Automation

\- Computer Vision

\- Deep Learning



\---



\## System Architecture



!\[Architecture](architecture/architecture.png)



\---



\## Dashboard Preview



!\[Dashboard](screenshots/dashboard.png)



\---



\## Intruder Detection Preview



!\[Intruder Detection](screenshots/intruder\_detected.png)



\---



\## Email Alert Preview



!\[Email Alert](screenshots/email\_alert.png)



\---



\## Captured Evidence Preview



!\[Captured Evidence](screenshots/capture\_example.png)



\---



\## Workflow



```text

Webcam

&#x20;  ↓

YOLOv8 detects a person

&#x20;  ↓

Face Recognition checks identity

&#x20;  ↓

Known person → No alert

Unknown person → Intruder detected

&#x20;  ↓

Capture image

&#x20;  ↓

Log event

&#x20;  ↓

Play alarm

&#x20;  ↓

Send email alert

&#x20;  ↓

Update dashboard

&#x20;  ↓

Remote monitoring on the phone



\# Project Structure

AI-Smart-Security-System
│
├── architecture/
│   └── architecture.png
│
├── screenshots/
│   ├── dashboard.png
│   ├── intruder_detected.png
│   ├── email_alert.png
│   └── capture_example.png
│
├── captures/
├── dashboard.py
├── face_security.py
├── email_alert.py
├── alarm.wav
├── events.txt
├── .gitignore
└── README.md




\# How to Run
\## 1. Clone the repository

git clone https://github.com/Pavanteja1706/AI-Smart-Security-System.git
cd AI-Smart-Security-System


\## Create and activate virtual environment

python -m venv venv
venv\Scripts\activate

\## Install dependencies

pip install -r requirements.txt

\## Run the dashboard

python dashboard.py

\## Open in browser

http://127.0.0.1:5000




\# Use Case

This project can be used for:

Smart home monitoring

Intruder detection

Evidence capture and alerting

AI-based surveillance research

Computer vision portfolio projects



\# Future Improvements

Mobile push notifications

Cloud storage for evidence images

Multi-camera support

Automatic incident report generation

User authentication for dashboard access

Alert history database


\# License

This project is for educational and portfolio purposes.




\# Creator

Pavan Teja Jukanti
Email Id: pavantejajukanti@gmail.com