# CityPortal — Community Issue Reporting & Tracking System

> **Dissertation Project** | Evaluating Agile Software Development Methodologies in Modern Software Engineering Projects

---

## Overview

CityPortal is a web-based community issue reporting and tracking portal built as part of a dissertation evaluating the effectiveness of Agile software development methodologies. The system allows residents to report local infrastructure problems (potholes, broken streetlights, garbage, waterlogging) and enables municipal admin officers to manage, prioritise, and resolve those issues in real time.

The project was developed iteratively across five Agile sprints using Scrum methodology, serving as a real-world artefact to validate the thematic analytical framework constructed through systematic literature review.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.0 |
| Database | SQLite (via Flask-SQLAlchemy) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Icons | Font Awesome 6.5 |
| Charts | Chart.js 4.4 |
| PDF Export | ReportLab |
| Authentication | Flask-Login (session-based) |
| File Uploads | Werkzeug + local storage |

---

## User Roles

### Resident
- Self-register and log in
- Submit community issues with photo, location, category
- Track real-time status of reported issues
- Receive in-app notifications on status updates
- Submit feedback and star rating after resolution

### Admin (Municipal Officer)
- Pre-created account (no public registration)
- View and manage all submitted issues
- Filter issues by status, category, priority, area
- Update issue status, set priority, add public/internal notes
- View analytics dashboard with charts
- Export analytics report as PDF
- Log Agile sprint entries for dissertation documentation

---

## Default Admin Credentials

```
Email:    admin@cityportal.com
Password: Admin@1234
```

> These credentials are auto-inserted into the database on first run. No manual setup required.

---

## Project Structure

```
community_portal/
│
├── app.py                        # Main Flask app — all routes
├── config.py                     # App configuration
├── database.py                   # SQLAlchemy models
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── static/
│   ├── css/
│   │   ├── main.css              # Global styles, shared components
│   │   ├── index.css             # Landing page styles
│   │   ├── auth.css              # Login and register styles
│   │   ├── resident.css          # Resident dashboard styles
│   │   └── admin.css             # Admin panel styles
│   │
│   ├── js/
│   │   ├── main.js               # Alerts, notification badge polling
│   │   ├── resident.js           # Photo upload and preview
│   │   ├── admin.js              # Filter submit, resolve confirmation
│   │   └── charts.js             # Chart.js bar, doughnut, line charts
│   │
│   ├── uploads/                  # Resident-uploaded issue photos
│   └── images/                   # Static images (logo, etc.)
│
├── templates/
│   ├── base.html                 # Master layout with navbar and footer
│   ├── index.html                # Public landing page
│   │
│   ├── auth/
│   │   ├── login.html            # Login page (both roles)
│   │   └── register.html         # Resident self-registration
│   │
│   ├── resident/
│   │   ├── dashboard.html        # Resident home with issue list
│   │   ├── report.html           # Submit new issue form
│   │   ├── issue_detail.html     # Issue status timeline view
│   │   ├── feedback.html         # Star rating feedback form
│   │   └── notifications.html    # Alert history page
│   │
│   └── admin/
│       ├── dashboard.html        # Admin summary with recent issues
│       ├── issues.html           # All issues with filters and search
│       ├── issue_detail.html     # Issue management and update form
│       ├── analytics.html        # Charts and metrics page
│       └── sprint_log.html       # Agile sprint documentation panel
│

```

---

## Database Models

| Model | Description |
|---|---|
| `User` | Stores both residents and admin with role field |
| `Issue` | Community issue with status, category, priority, photo |
| `StatusHistory` | Logs every status change with timestamp and note |
| `Feedback` | Resident star rating and comment after resolution |
| `Notification` | In-app alerts sent to residents on status change |

---

## Issue Status Flow

```
Submitted → Under Review → In Progress → Resolved → Closed
```

- **Submitted** — created by resident
- **Under Review** — admin has acknowledged
- **In Progress** — work has started
- **Resolved** — admin marks complete, resident is notified and prompted for feedback
- **Closed** — resident submits feedback, issue is fully closed

---

## Installation & Setup

### 1. Prerequisites

Make sure Python 3.8 or above is installed on your machine.

```bash
python --version
```

### 2. Clone or Extract the Project

If downloaded as a zip, extract it to your desired location.

```bash
cd community_portal
```

### 3. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The app will start at:

```
http://127.0.0.1:5000
```

The SQLite database (`community.db`) and the default admin account are created automatically on first run. No additional configuration is needed.

---

## Pages and URLs

| URL | Access | Description |
|---|---|---|
| `/` | Public | Landing page |
| `/login` | Public | Login for both roles |
| `/register` | Public | Resident registration |
| `/logout` | Logged in | Logout |
| `/resident/dashboard` | Resident | Issue list and summary |
| `/resident/report` | Resident | Submit new issue |
| `/resident/issue/<id>` | Resident | View issue detail and timeline |
| `/resident/feedback/<id>` | Resident | Submit feedback after resolution |
| `/resident/notifications` | Resident | View all alerts |
| `/admin/dashboard` | Admin | Summary and recent issues |
| `/admin/issues` | Admin | All issues with filter/search |
| `/admin/issue/<id>` | Admin | Manage individual issue |
| `/admin/analytics` | Admin | Charts and metrics |
| `/admin/export-pdf` | Admin | Download analytics PDF |

---

## Features Summary

### Resident Features
- Register and log in securely
- Submit issues with title, category, location, description, and photo
- Live photo preview before submission with drag-and-drop support
- Track issue status through a visual timeline
- Receive notifications when admin updates status
- Rate resolution with a 1–5 star system and optional comment

### Admin Features
- Pre-created account, no registration needed
- View all issues with colour-coded status and priority badges
- Overdue issues (unresolved beyond 7 days) highlighted automatically
- Filter by status, category, priority; search by title
- Update status, set priority, write public and internal notes
- Auto-notification sent to resident on every status change
- Confirm dialog before marking an issue as Resolved
- Analytics page with bar, doughnut, and line charts via Chart.js
- One-click PDF export of analytics report

---
