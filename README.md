# Sollar Installer

<div align="center">

### Intelligent Solar Lead Generation & Installer Management Platform

**Discover qualified homeowners • Score solar opportunities • Connect installers • Track leads**

[Live Demo](YOUR_RENDER_URL_HERE) · [GitHub Repository](https://github.com/jasminefloraa/Sollar_installer)

</div>

---

## Overview

**Sollar Installer** is a full-stack solar lead generation and installer management platform designed to connect high-potential homeowners with solar installation companies.

The platform transforms a homeowner's solar assessment into a structured, scored lead that installers can discover, claim, manage, and follow through a centralized dashboard.

Instead of manually handling leads, the system provides an end-to-end workflow:

**Homeowner Assessment → Solar Estimate → Lead Creation → Lead Scoring → Installer Discovery → Lead Claiming → Contact Unlock → Status Tracking**

---

## Problem

Solar installers often spend significant time identifying potential customers, evaluating lead quality, following up with homeowners, and maintaining lead pipelines.

Sollar Installer addresses this by providing a centralized system that:

* Collects homeowner solar assessment data
* Calculates estimated solar potential
* Assigns a lead score
* Categorizes lead potential
* Connects qualified leads with installers
* Provides installer dashboards
* Tracks lead status and notifications
* Supports real-time application updates

---

## Key Features

### Homeowner Assessment

Homeowners can submit information about their property and energy usage to generate a personalized solar opportunity estimate.

The system evaluates factors such as:

* Location
* Property information
* Electricity usage
* Roof information
* Solar suitability

### Intelligent Lead Scoring

Each homeowner is converted into a structured lead with:

* Lead score
* Potential category
* Estimated system size
* Estimated annual savings
* Payback period
* Estimated CO₂ reduction

Example:

```text
Lead ID:              SL-2026-000002
Location:             Dallas, TX 75001
Potential:            High Potential
Lead Score:           100
Estimated System:     7.7 kW
Annual Savings:       $2,160
Payback Period:       7 years
CO₂ Reduction:        4.2 t/year
```

### Installer Dashboard

Installers can:

* View available leads
* Filter and evaluate opportunities
* Claim leads
* Unlock homeowner contact information
* Update lead status
* Monitor notifications
* Track their pipeline

### Admin Dashboard

Administrators can monitor:

* Lead pipeline
* Installer accounts
* Lead assignments
* Platform analytics
* Lead status
* Notifications

### Real-Time Updates

The platform uses **Flask-SocketIO** for real-time communication and dashboard updates.

This allows important lead and notification events to be reflected without requiring constant manual page refreshes.

---

## Application Workflow

```text
                    HOMEOWNER
                        │
                        ▼
              Solar Assessment
                        │
                        ▼
                Solar Estimation
                        │
                        ▼
                 Lead Generation
                        │
                        ▼
                 Lead Scoring
                        │
                        ▼
              ┌─────────────────┐
              │   Lead Pipeline │
              └─────────────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        Installer A           Installer B
             │                     │
             └──────────┬──────────┘
                        ▼
                  Claim Lead
                        │
                        ▼
                Unlock Contact
                        │
                        ▼
                 Follow-up
                        │
                        ▼
                 Status Update
```

---

## Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-SocketIO
* SQLAlchemy
* PyJWT
* Flask-CORS
* Gunicorn

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive dashboard UI

### Database

* SQLite
* SQLAlchemy ORM

### Real-Time Communication

* Socket.IO
* WebSocket / polling support

### Deployment

* Render
* GitHub

---

## API Architecture

The backend follows a REST-style API structure.

### Authentication

```text
POST /api/auth/login
```

### Homeowner

```text
POST /api/homeowner/assessment
```

### Leads

```text
GET    /api/leads
PATCH  /api/leads/<id>
POST   /api/leads/<id>/claim
POST   /api/leads/<id>/assign
DELETE /api/leads/<id>
```

### Installers

```text
GET /api/installers
```

### Notifications

```text
GET   /api/notifications
PATCH /api/notifications/<id>/read
```

### Analytics

```text
GET /api/analytics/dashboard
```

### Health Check

```text
GET /api/health
```

### Real-Time

```text
/socket.io/
```

---

## Authentication

The application uses JWT-based authentication for protected API operations.

Different user roles can access different parts of the platform.

### Demo Accounts

#### Installer

```text
Email:    demo@installer.com
Password: Installer@123
```

#### Admin

```text
Email:    admin@sunlead.com
Password: Admin@123
```

> These credentials are provided for demonstration purposes.

---

## Project Structure

```text
Sollar_installer/
│
├── app.py
│
├── static/
│   └── index.html
│
├── instance/
│   └── sunlead.db
│
├── requirements.txt
│
└── .gitignore
```

The local SQLite database is intentionally excluded from version control.

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/jasminefloraa/Sollar_installer.git
cd Sollar_installer
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## Deployment

The application is configured for deployment on Render.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn --threads 100 app:app
```

The production server runs the Flask application through Gunicorn while supporting the application's Socket.IO configuration.

---

## Example Lead

A sample high-potential lead generated by the platform:

| Attribute      | Value          |
| -------------- | -------------- |
| Lead ID        | SL-2026-000002 |
| Location       | Dallas, TX     |
| ZIP Code       | 75001          |
| Potential      | High Potential |
| Score          | 100            |
| System Size    | 7.7 kW         |
| Annual Savings | $2,160         |
| Payback        | 7 years        |
| CO₂ Reduction  | 4.2 t/year     |

---

## Why This Project?

Sollar Installer demonstrates practical full-stack development rather than being only a static interface.

The project combines:

* REST API development
* Authentication
* Database modeling
* CRUD operations
* Role-based workflows
* Real-time communication
* Business logic
* Lead scoring
* Dashboard development
* Deployment
* Git/GitHub workflow

---

## Engineering Highlights

### Full-Stack Architecture

The application connects a browser-based dashboard with a Flask backend and relational data layer.

### API-First Design

Core functionality is exposed through structured REST endpoints, making the system easier to extend or integrate with external services.

### Real-Time Communication

Flask-SocketIO enables real-time events for notifications and application updates.

### Role-Based Workflow

The system separates homeowner, installer, and administrator workflows to reflect a realistic business platform.

### Lead Lifecycle Management

Leads move through a defined lifecycle:

```text
New
 ↓
Available
 ↓
Claimed
 ↓
Contact Unlocked
 ↓
Follow-up
 ↓
Converted / Closed
```

---

## Future Improvements

Potential future enhancements include:

* PostgreSQL production database
* Persistent cloud storage
* Email automation
* SMS notifications
* Advanced lead scoring models
* Installer matching based on location
* Google Maps integration
* Payment and subscription functionality
* Advanced analytics
* Automated follow-up campaigns
* Production-grade authentication and security hardening

---

## Project Status

**Status:** Deployed / Deployment in Progress

The application is actively being developed and prepared for production deployment.

---

## Author

### Jasmine Flora J

B.Tech Computer Science & Engineering
Manakula Vinayagar Institute of Technology

GitHub:
https://github.com/jasminefloraa

LinkedIn:
https://www.linkedin.com/in/jasmine-flora/

---

<div align="center">

### Sollar Installer

**Turning solar interest into qualified opportunities.**

Built with Python, Flask, SQLAlchemy, JavaScript and Socket.IO.

</div>
# Sollar Installer

<div align="center">

### Intelligent Solar Lead Generation & Installer Management Platform

**Discover qualified homeowners • Score solar opportunities • Connect installers • Track leads**

[Live Demo](YOUR_RENDER_URL_HERE) · [GitHub Repository](https://github.com/jasminefloraa/Sollar_installer)

</div>

---

## Overview

**Sollar Installer** is a full-stack solar lead generation and installer management platform designed to connect high-potential homeowners with solar installation companies.

The platform transforms a homeowner's solar assessment into a structured, scored lead that installers can discover, claim, manage, and follow through a centralized dashboard.

Instead of manually handling leads, the system provides an end-to-end workflow:

**Homeowner Assessment → Solar Estimate → Lead Creation → Lead Scoring → Installer Discovery → Lead Claiming → Contact Unlock → Status Tracking**

---

## Problem

Solar installers often spend significant time identifying potential customers, evaluating lead quality, following up with homeowners, and maintaining lead pipelines.

Sollar Installer addresses this by providing a centralized system that:

* Collects homeowner solar assessment data
* Calculates estimated solar potential
* Assigns a lead score
* Categorizes lead potential
* Connects qualified leads with installers
* Provides installer dashboards
* Tracks lead status and notifications
* Supports real-time application updates

---

## Key Features

### Homeowner Assessment

Homeowners can submit information about their property and energy usage to generate a personalized solar opportunity estimate.

The system evaluates factors such as:

* Location
* Property information
* Electricity usage
* Roof information
* Solar suitability

### Intelligent Lead Scoring

Each homeowner is converted into a structured lead with:

* Lead score
* Potential category
* Estimated system size
* Estimated annual savings
* Payback period
* Estimated CO₂ reduction

Example:

```text
Lead ID:              SL-2026-000002
Location:             Dallas, TX 75001
Potential:            High Potential
Lead Score:           100
Estimated System:     7.7 kW
Annual Savings:       $2,160
Payback Period:       7 years
CO₂ Reduction:        4.2 t/year
```

### Installer Dashboard

Installers can:

* View available leads
* Filter and evaluate opportunities
* Claim leads
* Unlock homeowner contact information
* Update lead status
* Monitor notifications
* Track their pipeline

### Admin Dashboard

Administrators can monitor:

* Lead pipeline
* Installer accounts
* Lead assignments
* Platform analytics
* Lead status
* Notifications

### Real-Time Updates

The platform uses **Flask-SocketIO** for real-time communication and dashboard updates.

This allows important lead and notification events to be reflected without requiring constant manual page refreshes.

---

## Application Workflow

```text
                    HOMEOWNER
                        │
                        ▼
              Solar Assessment
                        │
                        ▼
                Solar Estimation
                        │
                        ▼
                 Lead Generation
                        │
                        ▼
                 Lead Scoring
                        │
                        ▼
              ┌─────────────────┐
              │   Lead Pipeline │
              └─────────────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        Installer A           Installer B
             │                     │
             └──────────┬──────────┘
                        ▼
                  Claim Lead
                        │
                        ▼
                Unlock Contact
                        │
                        ▼
                 Follow-up
                        │
                        ▼
                 Status Update
```

---

## Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-SocketIO
* SQLAlchemy
* PyJWT
* Flask-CORS
* Gunicorn

### Frontend

* HTML5
* CSS3
* JavaScript
* Responsive dashboard UI

### Database

* SQLite
* SQLAlchemy ORM

### Real-Time Communication

* Socket.IO
* WebSocket / polling support

### Deployment

* Render
* GitHub

---

## API Architecture

The backend follows a REST-style API structure.

### Authentication

```text
POST /api/auth/login
```

### Homeowner

```text
POST /api/homeowner/assessment
```

### Leads

```text
GET    /api/leads
PATCH  /api/leads/<id>
POST   /api/leads/<id>/claim
POST   /api/leads/<id>/assign
DELETE /api/leads/<id>
```

### Installers

```text
GET /api/installers
```

### Notifications

```text
GET   /api/notifications
PATCH /api/notifications/<id>/read
```

### Analytics

```text
GET /api/analytics/dashboard
```

### Health Check

```text
GET /api/health
```

### Real-Time

```text
/socket.io/
```

---

## Authentication

The application uses JWT-based authentication for protected API operations.

Different user roles can access different parts of the platform.

### Demo Accounts

#### Installer

```text
Email:    demo@installer.com
Password: Installer@123
```

#### Admin

```text
Email:    admin@sunlead.com
Password: Admin@123
```

> These credentials are provided for demonstration purposes.

---

## Project Structure

```text
Sollar_installer/
│
├── app.py
│
├── static/
│   └── index.html
│
├── instance/
│   └── sunlead.db
│
├── requirements.txt
│
└── .gitignore
```

The local SQLite database is intentionally excluded from version control.

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/jasminefloraa/Sollar_installer.git
cd Sollar_installer
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the application

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## Deployment

The application is configured for deployment on Render.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn --threads 100 app:app
```

The production server runs the Flask application through Gunicorn while supporting the application's Socket.IO configuration.

---

## Example Lead

A sample high-potential lead generated by the platform:

| Attribute      | Value          |
| -------------- | -------------- |
| Lead ID        | SL-2026-000002 |
| Location       | Dallas, TX     |
| ZIP Code       | 75001          |
| Potential      | High Potential |
| Score          | 100            |
| System Size    | 7.7 kW         |
| Annual Savings | $2,160         |
| Payback        | 7 years        |
| CO₂ Reduction  | 4.2 t/year     |

---

## Why This Project?

Sollar Installer demonstrates practical full-stack development rather than being only a static interface.

The project combines:

* REST API development
* Authentication
* Database modeling
* CRUD operations
* Role-based workflows
* Real-time communication
* Business logic
* Lead scoring
* Dashboard development
* Deployment
* Git/GitHub workflow

---

## Engineering Highlights

### Full-Stack Architecture

The application connects a browser-based dashboard with a Flask backend and relational data layer.

### API-First Design

Core functionality is exposed through structured REST endpoints, making the system easier to extend or integrate with external services.

### Real-Time Communication

Flask-SocketIO enables real-time events for notifications and application updates.

### Role-Based Workflow

The system separates homeowner, installer, and administrator workflows to reflect a realistic business platform.

### Lead Lifecycle Management

Leads move through a defined lifecycle:

```text
New
 ↓
Available
 ↓
Claimed
 ↓
Contact Unlocked
 ↓
Follow-up
 ↓
Converted / Closed
```

---

## Future Improvements

Potential future enhancements include:

* PostgreSQL production database
* Persistent cloud storage
* Email automation
* SMS notifications
* Advanced lead scoring models
* Installer matching based on location
* Google Maps integration
* Payment and subscription functionality
* Advanced analytics
* Automated follow-up campaigns
* Production-grade authentication and security hardening

---

## Project Status

**Status:** Deployed / Deployment in Progress

The application is actively being developed and prepared for production deployment.

---

## Author

### Jasmine Flora J

B.Tech Computer Science & Engineering
Manakula Vinayagar Institute of Technology

GitHub:
https://github.com/jasminefloraa

LinkedIn:
https://www.linkedin.com/in/jasmine-flora/

---

<div align="center">

### Sollar Installer

**Turning solar interest into qualified opportunities.**

Built with Python, Flask, SQLAlchemy, JavaScript and Socket.IO.

</div>
