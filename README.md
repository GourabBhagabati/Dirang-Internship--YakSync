# 🐄 YakSync: Precision Livestock & IoT Management

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-4.2.7-green.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Firebase Integration](https://img.shields.io/badge/Firebase-Active-orange.svg?style=for-the-badge&logo=firebase&logoColor=white)](https://firebase.google.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

YakSync is an enterprise-grade IoT-driven digital livestock management platform developed under the **Dirang Valley Initiative**—a smart agriculture program aimed at transforming traditional highland livestock farming in the Himalayan region.

The platform provides farmers, veterinarians, and administrators with a unified, intelligent interface to monitor animals, manage IoT-connected sensors, track veterinary treatment protocols, oversee hormone administration workflows, and respond to critical system alerts—all from a single, responsive web dashboard.

---

## 🗺️ System Architecture

```
[Collars/Sensors on Yak] 
          │ 
          ▼ (Wi-Fi / IoT Network)
[Cloud Firestore / Realtime DB] ◄───► [Django Web App Container] (Backed by SQLite)
          │                                     │
          ▼ (Real-time Telemetry)               ▼ (Reports, Audits, Admin)
[Interactive Dashboard Charts]        [Watermarked PDFs / Activity Logs]
```

---

## ✨ Key Features

### 🔐 Authentication & User Roles
* Secure login, registration, and session management.
* **Role-Based Access Control (RBAC)**: Supports **Administrator**, **Veterinarian**, and **Farm Operator** roles with customized view privileges.

### 🐄 Livestock Directory
* Dynamic animal profiles containing breed metadata, active health statuses, and complete event logs.
* Advanced search and filters targeting species types, active protocol assignees, and pasture locations.

### 📡 IoT Device Registry
* Track active collars, battery lives, and connectivity statuses.
* Seamless live status updates for all hardware components.

### 📊 Real-time Telemetry Dashboard
* Dynamic welcome banners, stats counts grids, and hormone reservoir tracking.
* **Interactive Charting**: A dynamic Chart.js timeline showing body temperature and movement steps.
* **Firebase Syncing**: Powered by Cloud Firestore (`onSnapshot`) for real-time telemetry streaming, falling back to local HTTP REST APIs if unconfigured.
* **Responsive Sidebar Layout**: Featuring a collapsible sidebar that persists its visual state (`open`/`closed`) in browser storage to prevent rendering flicker on reload.
* **Interactive Theme Toggle**: Built-in Light/Dark mode selector inside the navbar, featuring synchronized loading states.

### 💉 Hormone & Protocol Workflows
* **Hormone Reservoirs**: Real-time quantity monitors and usage logging.
* **Treatment Protocols**: Step-by-step definition templates (e.g., Ovsynch) with day-offsets, and automated assignments for animals.

### 🚨 Smart Alerts & Activity Logs
* Three-tier notification framework (**Critical**, **Warning**, **Info**) in the navigation bar.
* Live localized timestamps (configured under `Asia/Kolkata` time) in log grids.
* Compliance audit trials tracing user actions, modifications, and session events.

### 📄 Analytical Reports
* PDF exports with customized, transparent background watermarks (`YakBackground.png` rendered with 10% opacity) and CSV spreadsheet downloads.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Django 4.2.7 | Core MVT architectural layer & REST APIs |
| **Database** | SQLite3 | Local storage of users, metadata, and schedules |
| **Real-time Telemetry** | Google Firebase | Cloud Firestore for live telemetry streaming |
| **Frontend Styling** | HTML5 / Vanilla CSS3 | Responsive layout featuring custom Slate Dark Theme |
| **Charts** | Chart.js | Interactive telemetry plotting |
| **PDF Generation** | ReportLab 4.5.1 | Custom watermarked PDF compilation |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+
* Git

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/yaksync.git
   cd yaksync
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser Account**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Local Development Server**
   ```bash
   python manage.py runserver
   ```

Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## 👥 User Roles & Access Matrix

### 🛡️ Administrator (System Overlord)
* Manage platform users, role assignments, and system settings.
* Full access to livestock directory, device registers, and warning templates.
* Monitor activity logs, generate PDF/CSV reports, and execute database tasks.

### 🩺 Veterinarian (Health Specialist)
* Full access to animal medical histories and treatment logs.
* Define medical protocols, assign them to yaks, and log hormone administration.
* Monitor health-related alerts and execute diagnostic reports.

### 🌾 Farm Operator (Field Staff)
* Overview livestock status, location logs, and active alert notifications.
* Monitor device registries and update field statuses.
* Log basic pasture observations and daily activities (Read-only access to medical protocols).

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps to contribute:
1. **Fork** the repository.
2. Create a **Feature Branch**: `git checkout -b feature/your-feature-name`.
3. **Commit** your changes: `git commit -m 'Add: feature description'`.
4. **Push** to the branch: `git push origin feature/your-feature-name`.
5. Open a **Pull Request**.

---

## 📄 License
This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.
