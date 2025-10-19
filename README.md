## 🚀 Flask Backend – Authentication & Authorization System

### 📋 Overview

This backend is built using **Flask** and provides APIs for user authentication and authorization.
It supports secure registration and login functionality with role-based access (`admin`, `hospital`, and `ambulance`).
The backend connects to a SQL database using **SQLAlchemy** and integrates seamlessly with a React frontend.

---

### 🏗️ Tech Stack

* **Backend Framework:** Flask
* **ORM:** SQLAlchemy
* **Database:** SQLite (can be changed to MySQL/PostgreSQL)
* **Authentication:** JWT (JSON Web Tokens)
* **Authorization:** Role-based (`admin`, `hospital`, `ambulance`)
* **CORS:** Flask-CORS
* **Frontend:** React (connected via Axios)

---

### 📁 Project Structure

```
backend/
│
├── app/
│   ├── __init__.py           # App factory and configurations
│   ├── models.py             # Database models (User model, roles)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── auth_routes.py    # Register & Login routes
│
├── instance/
│   └── database.db           # SQLite database (auto-generated)
│
├── requirements.txt          # Dependencies
├── app.py                    # Entry point
└── README.md                 # Project documentation
```

---

### ⚙️ Installation & Setup

#### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd backend
```

#### 2. Create a virtual environment

```bash
python -m venv venv
```

#### 3. Activate the environment

* **Windows:**

  ```bash
  venv\Scripts\activate
  ```
* **macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

#### 4. Install dependencies

```bash
pip install -r requirements.txt
```

#### 5. Run the Flask app

```bash
flask run
```

By default, it runs at:
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### 🔐 API Endpoints

#### **POST** `/auth/register`

Registers a new user.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "role": "hospital"
}
```

**Response:**

```json
{
  "message": "User registered successfully"
}
```

---

#### **POST** `/auth/login`

Logs in an existing user and returns a JWT token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**

```json
{
  "token": "<JWT_TOKEN>",
  "role": "hospital"
}
```

---

### 🔗 Frontend Integration

The backend is designed to work with a React frontend running on
👉 `http://localhost:3000`

Make sure **CORS** is enabled in `app.py`:

```python
from flask_cors import CORS
CORS(app)
```

React will connect via:

```
http://127.0.0.1:5000/auth/register
http://127.0.0.1:5000/auth/login
```

---

### 🧠 Roles

* **Admin:** Full access to the system
* **Hospital:** Can access hospital-specific modules
* **Ambulance:** Limited access to dispatch features

---

### 🧩 Requirements File Example

Here’s what your `requirements.txt` may contain:

```
Flask
Flask-SQLAlchemy
Flask-Cors
PyJWT
```

---

### 🧾 License

This project is licensed under the **MIT License** – you’re free to modify and distribute it.

---

### 💬 Author

Developed by **[Athrava Wadhe]**
