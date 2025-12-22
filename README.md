# Django API & Web Application  
### JWT Authentication • Role-Based Access • Swagger Documentation

---

##  Overview
This project is a **Django-based backend application** with a **Django Templates frontend** and a **REST API secured using JWT authentication**.

The system implements **Dashboard and User Management** features with full CRUD operations and supports multiple user roles:
- **Admin**
- **Leader**
- **Burner**
- **User**

The project uses **Pipenv** for dependency management and provides **Swagger/OpenAPI documentation** for easy API testing.

---

##  Tech Stack

- **Backend:** Django, Django REST Framework
- **Frontend:** Django Templates & Static Files
- **Authentication:** JWT (JSON Web Tokens)
- **Authorization:** Role-Based Access Control (RBAC)
- **Documentation:** Swagger / OpenAPI
- **Environment Management:** Pipenv

---

##  Authentication & Authorization

### JWT Authentication
- Secure, stateless authentication using JWT
- Token must be sent with API requests:

# Authorization: Bearer <your_token>

### Role-Based Access Control

| Role   | Permissions |
|------|-------------|
| **Admin** | Full access to all APIs |
| **Leader** | Team management & reporting |
| **Burner** | Temporary / limited access |
| **User** | Personal profile management |

Access control is enforced using custom Django/DRF permissions.

---

##  API Features

### Supported HTTP Methods
- **GET** – Fetch dashboard data & user profiles
- **POST** – Create users and resources
- **PATCH** – Update profiles and settings
- **DELETE** – Remove resources (**Admin only**)

---

##  API Documentation (Swagger)

Interactive API documentation is available using Swagger UI.

###  Swagger URL

Features:
- Auto-generated request & response schemas
- JWT authorization support
- Role-protected endpoint testing

---

##  Frontend (Templates)

The frontend is rendered using Django templates and static files.

###  Frontend URL
# Install Dependencies
pipenv install
# Activate Virtual Environment
pipenv shell
# Start the Django development server
python manage.py runserver
# Access the application:
Frontend:http://127.0.0.1:8000/
API Docs (Swagger):http://127.0.0.1:8000/api/docs/
