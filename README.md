# 🐄 Dairy Cow Monitoring & Milk Yield Prediction Backend

## 📖 Overview
This project is a **Flask-based backend system** designed for monitoring dairy cows using **IoT sensors** and applying **machine learning models** to predict milk yield and detect potential health issues.  

It was developed as part of an **IoT + AI-driven dairy farm management system**.  
The backend acts as the **bridge between IoT devices, machine learning models, and frontend applications (Flutter mobile app)**.  

---

## 🎯 Objectives
- Collect **real-time sensor readings** (temperature, accelerometer, gyroscope) from cows.
- Provide a **REST API** for storing and retrieving cow health data.
- Use **ML/DL models** to:
  - Predict **milk yield** based on multiple factors.
  - Detect **abnormal activity patterns** (possible disease or stress).
- Provide **secure user authentication** (Firebase + JWT).
- Allow **admin monitoring** of users and cows.
- Be deployable on **Heroku / cloud services** for real-world scalability.

---

## 🚀 Features
✅ **User Authentication** – Firebase-based signup/login with JWT.  
✅ **Cow Profiles** – Add, view, and monitor cow health records.  
✅ **Milk Yield Prediction** – Hybrid ML model (`.h5` + scaler `.pkl`).  
✅ **Disease Prediction** – Detect unusual accelerometer/gyroscope readings.  
✅ **Firebase Integration** – Real-time database storage.  
✅ **Admin APIs** – Manage users and cows centrally.  
✅ **Charts & Visualization Support** – API endpoints return data for plotting.  
✅ **Cron Jobs** – Background jobs for automated tasks.  
✅ **Logging** – Centralized logging for debugging & monitoring.  

---

app/
│── init.py
│── auth/ # User authentication APIs
│── admin/ # Admin functionalities
│── cows/ # Cow profile & monitoring APIs
│── disease_prediction/ # Disease detection logic
│── mLmodel/ # ML models (milk yield, preprocessing)
│── models/ # Pre-trained models, scalers, configs
│── user_profile/ # User profile management
│── utils/ # Helpers (logging, auth, decorators, sensor utils)
│── cronjob/ # Scheduler for periodic tasks
run.py # App entry point
requirements.txt # Python dependencies
Procfile # Heroku deployment config
runtime.txt # Python runtime version
