Hybrid Web + Desktop Application

A full-stack hybrid application for visualizing, analyzing, and reporting chemical equipment parameters using a shared Django REST backend, a React web dashboard, and a PyQt5 desktop application.

🚀 Project Overview

This project allows users to upload a CSV file containing chemical equipment data such as:

Equipment Name

Equipment Type

Flowrate

Pressure

Temperature

The backend processes the data, computes analytics, and exposes APIs that are consumed by both Web and Desktop clients.



React (Web)        PyQt5 (Desktop)
     │                    │
     └──── REST API ──────┘
              │
        Django + DRF
              │
           Pandas



🛠 Tech Stack
Backend

Django 4.2

Django REST Framework

Pandas

SQLite

Gunicorn

Render (Deployment)

Frontend (Web)

React.js

Chart.js

Vercel (Deployment)

Frontend (Desktop)





Key Features

📂 CSV Upload (Web + Desktop)

📊 Interactive Charts & Graphs

📋 Equipment Data Table

📈 Summary Statistics

Total equipment count

Average flowrate

Average pressure

Average temperature

🧾 PDF Report Generation

🔐 Authentication (Admin)

🕓 Dataset History (last 5 uploads)




chemical-equipment-visualizer/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── analyticsapp/
│   ├── api/
│   └── backend/
│
├── frontend-web/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── frontend-desktop/
│   ├── main.py
│   └── requirements.txt
│
├── README.md
└── .gitignore



Backend Setup (Local)
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


API will be available at:
http://127.0.0.1:8000/api/



Web Frontend Setup (Local)
cd frontend-web
npm install
npm run dev


Desktop Application Setup
cd frontend-desktop
pip install -r requirements.txt
python main.py


Sample CSV Format
Equipment Name,Type,Flowrate,Pressure,Temperature
Heat Exchanger HX-101,Heat Exchanger,250,15,180
Centrifugal Pump P-201,Pump,180,25,65


Deployment Notes

Backend uses Python 3.11 (via runtime.txt)

Pandas & NumPy versions pinned for cloud compatibility

Same REST API consumed by both Web & Desktop clients


## 🎥 Demo Video

A short demo video demonstrating the complete working of the project:

🔗 https://www.loom.com/share/840fbfc58c9d42a4a1f9463ecf4a0b21


The demo covers:
- GitHub repository overview
- Backend API functionality
- Web application (CSV upload, charts, analytics)
- Desktop application (PyQt5 interface and visualization)



















PyQt5

Matplotlib
