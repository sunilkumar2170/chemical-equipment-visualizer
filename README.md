Chemical Equipment Visualizer
Hybrid Web + Desktop Application
A full-stack hybrid application for visualizing, analyzing, and reporting chemical equipment parameters using a shared Django REST backend, React web dashboard, and PyQt5 desktop application.

🚀 Quick Demo
Watch Demo Video
demo link-https://www.loom.com/share/840fbfc58c9d42a4a1f9463ecf4a0b21



(Shows complete workflow: CSV upload → Backend processing → Web/Desktop visualization)

📋 Features
📂 CSV Upload (Web + Desktop) - Upload equipment data instantly

📊 Interactive Charts - Flowrate, Pressure, Temperature visualizations

📈 Real-time Analytics

Total equipment count

Average flowrate, pressure, temperature

🧾 PDF Reports - Download professional analytics reports

🔐 Admin Authentication - Secure data management

🕓 Upload History - Track last 5 dataset uploads

🛠 Tech Stack
text
Frontend (Web)    → React.js + Chart.js + Vercel
Frontend (Desktop)→ PyQt5 + Matplotlib
Backend           → Django 4.2 + DRF + Pandas + SQLite + Render
Deployment        → Shared REST API for both clients
📁 Project Structure
text
chemical-equipment-visualizer/
├── backend/                 # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   └── analyticsapp/
├── frontend-web/            # React Dashboard
│   ├── src/
│   └── package.json
├── frontend-desktop/        # PyQt5 Desktop App
│   ├── main.py
│   └── requirements.txt
├── README.md
└── equipment_data.csv       # Sample data
🎯 Sample CSV Format
text
Equipment Name,Type,Flowrate,Pressure,Temperature
HX-101,Heat Exchanger,250,15,180
P-201,Pump,180,25,65
V-301,Vessel,0,10,90
C-401,Compressor,350,30,120
🚀 Quick Setup (5 Minutes)
Backend (Django API)
bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
API Ready: http://127.0.0.1:8000/api/

Web Frontend (React)
bash
cd frontend-web
npm install
npm run dev
Web Ready: http://localhost:5173

Desktop App (PyQt5)
bash
cd frontend-desktop
pip install -r requirements.txt
python main.py
🔗 Live Deployment Links
text
Backend API: https://chemical-visualizer-api.onrender.com/api/
Web App:     https://chemical-visualizer-web.vercel.app/
Desktop:     Download .exe from Releases
📊 API Endpoints
text
GET  /api/analytics/          # Summary statistics + data
POST /api/upload/             # CSV upload endpoint  
GET  /api/history/            # Last 5 uploads
GET  /api/export/pdf/         # PDF report download
🐛 Troubleshooting
Backend not starting? → Check Python 3.11 + pip install pandas==1.24.0

CORS issues? → Backend auto-configured for localhost

Charts not loading? → Backend API must be running first

Desktop blank? → Check backend URL in main.py

🤝 Contributing
Fork repository

Create feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add some AmazingFeature')

Push & Open PR

📄 License
MIT License - Free to use/modify/deploy anywhere!

👨‍💻 Author
Sunil Kumar
GitHub | LinkedIn
