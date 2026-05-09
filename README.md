# 🚀 Smart Task Management System

A robust, full-stack Task Management web application built with **Flask**, **PostgreSQL**, and **WebSockets**. This project features a modern glassmorphism UI, real-time synchronization, and advanced data analytics.

---

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Folder Structure](#-folder-structure)
- [Installation & Setup](#-installation--setup)
- [PostgreSQL Setup](#-postgresql-setup)
- [Environment Variables](#-environment-variables-setup)
- [API Endpoints](#-api-endpoints)
- [WebSocket Implementation](#-websocket-explanation)
- [Analytics Logic](#-analytics-explanation)
- [Future Improvements](#-future-improvements)
- [Author](#-author)

---

## 🔍 Project Overview
The **Smart Task Management System** is designed to help users organize their daily tasks efficiently. It provides a secure environment for task creation, tracking, and analysis. With real-time updates, users can see changes instantly across multiple devices or tabs without refreshing the page.

## ✨ Key Features
- **Secure Authentication**: User registration and login with encrypted passwords (Bcrypt) and session management.
- **Real-Time Synchronization**: Live task updates (Add/Edit/Delete) powered by Socket.IO.
- **Advanced Analytics**: Interactive dashboard showing task distribution by status, priority, and daily productivity trends.
- **RESTful API**: Fully documented API for integration with other services.
- **Premium UI**: Modern, responsive design featuring glassmorphism effects and smooth transitions.
- **Input Validation**: Strict server-side validation for emails, passwords, and task details.

## 🛠️ Tech Stack
- **Backend**: Python 3.x, Flask, Flask-SocketIO, Flask-Bcrypt
- **Database**: PostgreSQL, Psycopg2
- **Data Science**: Pandas, NumPy (for analytics processing)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Configuration**: Python-Dotenv for environment security

## 📸 Screenshots
*(Add your project screenshots here)*

| Dashboard | Task Management |
| :---: | :---: |
| ![Dashboard Placeholder](https://via.placeholder.com/400x250?text=Dashboard+UI) | ![Task UI Placeholder](https://via.placeholder.com/400x250?text=Task+Management) |

## 📁 Folder Structure
```text
task_management/
├── static/
│   ├── css/          # Custom stylesheets
│   └── js/           # Frontend logic & WebSocket client
├── templates/        # HTML templates (Jinja2)
├── analytics.py      # Pandas & NumPy logic for stats
├── app.py            # Main Flask application & API routes
├── config.py         # Environment configuration loader
├── models.py         # Database connection & table creation
├── schema.sql        # Database schema definitions
├── .env.example      # Template for environment variables
├── .gitignore        # Git ignore rules for public upload
├── requirements.txt  # Project dependencies
└── README.md         # Project documentation
```

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/task-management.git
   cd task-management
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🐘 PostgreSQL Setup

1. **Create the Database**:
   Log in to your PostgreSQL terminal or pgAdmin and run:
   ```sql
   CREATE DATABASE task_management_db;
   ```

2. **Verify Schema**:
   The application automatically creates tables (`users`, `tasks`) on the first run using `schema.sql`.

## 🔐 Environment Variables Setup

Create a `.env` file in the root directory and configure your credentials. **Do not commit this file to GitHub.**

```env
DB_HOST=localhost
DB_NAME=task_management_db
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_PORT=5432
SECRET_KEY=your_generated_secret_key
```

## 🚀 Running Locally

```bash
python app.py
```
The server will start at `http://127.0.0.1:5000`.

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | User registration |
| `POST` | `/login` | User authentication |
| `GET` | `/api/tasks` | Fetch all tasks for current user |
| `POST` | `/api/tasks` | Create a new task |
| `PUT` | `/api/tasks/<id>` | Update an existing task |
| `DELETE` | `/api/tasks/<id>` | Delete a task |
| `GET` | `/api/analytics` | Get task statistics |

## 🔄 WebSocket Explanation
The project uses **Flask-SocketIO** to maintain a persistent connection between the server and clients.
- **Events Emitted**: `task_added`, `task_updated`, `task_deleted`.
- **Benefit**: Whenever a user modifies a task, the server broadcasts the change to all active sessions, ensuring data consistency without manual refreshes.

## 📊 Analytics Explanation
The analytics engine leverages **Pandas** and **NumPy**:
- **Data Processing**: Tasks are loaded into a Pandas DataFrame for efficient filtering and grouping.
- **NumPy Calculations**: Used for calculating completion percentages and average daily task counts.
- **Insights**: Provides breakdown by priority (Low, Medium, High) and status (Pending, In Progress, Completed).

## 🔮 Future Improvements
- [ ] Integration with Google Calendar API.
- [ ] Dark/Light mode toggle.
- [ ] Email notifications for upcoming deadlines.
- [ ] Drag-and-drop task reordering.

## 👤 Author
**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---
*Developed with ❤️ for Task Management Excellence.*
