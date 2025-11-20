# 📘 Kelaasor_advance

### A Complete Django REST Framework Backend for Online Bootcamps & Learning Platform

---

## 🚀 Overview

**Advance Kelaasor** is the backend system powering an online learning platform designed for hosting specialized bootcamps, online courses, and offline video courses.
This platform is part of the **Kelaasor ecosystem** and provides a robust infrastructure for:

* Managing courses (online/offline)
* User authentication via OTP
* Shopping cart & checkout
* Group purchases
* Ticketing & user support
* Admin dashboard for managing users, courses, discounts, and more

The project is fully built with **Django REST Framework**, **PostgreSQL**, and **Simple JWT**, and includes a complete Postman collection for testing.

---


# ✨ Key Features

## 🛒 Course Store

* Online courses with registration deadlines
* Offline/video courses with limited access period
* Rich course metadata:

  * Title, description, start date, duration
  * Instructors
  * Price & tiered pricing (for group purchases)
  * Images, videos, and attachments
* Support for chapters and multiple videos per chapter (for offline courses)
* Search, filter, and sort capabilities


## 👥 Users & Authentication

* Register and login via **OTP (SMS-based)**

* Token-based authentication using **Simple JWT** (access & refresh tokens)

* User profile completion before checkout (name, contact info, etc.)

* Shopping cart logic:

  * A user can only buy **one instance** of each course
  * A user **cannot re-purchase** a course they already own
  * Cart can contain multiple different courses

* Single and **group purchase** flows:

  * One user can buy a course for themselves and for multiple team members
  * Requires providing team members’ information

* User dashboard:

  * List of purchased courses
  * Order history
  * Payment history
  * Notifications & offers
  * Tickets and support messages


## 🎫 Ticketing System

* Create tickets:

  * General (not tied to a course)
  * Course-specific (linked to a purchased course)
* Ticket fields:

  * Message
  * Created date
  * Sender
  * Status
  * Department (financial, support, educational, etc.)
* Tickets can be public or tied to a specific course
* Users are notified (email/SMS) when a new reply is added to their ticket

## 🛠 Admin & Support Panel

* Role-based access using Django’s groups and permissions

  * Support team: access to tickets only
  * Product/content team: access to courses & categories
  * Admins: full access

* Course management:

  * Add courses with complete details
  * Edit/delete courses
  * Configure fixed prices and tiered group-pricing

* Discount code management:

  * Public codes or user-specific / course-specific codes
  * One-time or multi-use codes
  * Fixed amount or percentage-based
  * Valid only within a specific date range

* User & enrollment management:

  * Manually add/remove students from courses

* Ticket management:

  * View all tickets
  * Respond to user tickets

---


# 🧩 Tech Stack

| Component      | Technology                     |
| -------------- | ------------------------------ |
| Backend        | Django + Django REST Framework |
| Authentication | OTP + Simple JWT               |
| Database       | PostgreSQL                     |
| Async/Tasks    | Celery + Redis (optional)      |
| Docs/Testing   | Postman Collection             |

---


# 📁 Project Structure (Simplified)

```bash
kelaasor_advance/
├── users/
├── courses/
├── purchase/
├── tickets/
├── user_panel/
├── admin_panel/
├── kelaasor_advance/
│   ├── settings.py
│   └── urls.py
└── manage.py
```

---


# 🔐 Authentication Flow

### 1️⃣ OTP Login

* `POST /api/users/send-otp/`
* `POST /api/users/verify-otp/` → returns `access` and `refresh` tokens

### 2️⃣ Simple JWT

* `POST /api/users/token/`
* `POST /api/users/token/refresh/`

All authenticated requests use:

```http
Authorization: Bearer <access_token>
```

---


# 📮 Postman Collection

The repository includes a **full Postman collection** that covers:

* Users (Auth + OTP + JWT)
* Course catalog (public endpoints)
* Cart & orders & checkout
* Discounts
* Tickets
* User panel
* Admin panel

Files (included in the repo):

* `kelaasor_postman_collection_latest.json`
* `kelaasor_postman_environment_latest.json`

The environment includes variables for:

* `base_url`
* `mobile`
* `otp_code`
* `access_token`
* `refresh_token`

Collection-level scripts automatically store JWT tokens after OTP verification or login.

---


# ⚙️ Environment Setup

Create a `.env` file in the project root:

```dotenv
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=kelaasor_db
DB_USER=kelaasor_user
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432

TIME_ZONE=Asia/Tehran

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@kelaasor.com
```

> For production, set `DEBUG=False`, configure a real SMTP backend, strict `ALLOWED_HOSTS`, and secure secrets via environment variables or a secret manager.

---


# ▶️ Running the Project

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Apply migrations

```bash
python manage.py migrate
```

## 3. Create a superuser

```bash
python manage.py createsuperuser
```

## 4. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000/
```

---

# 🧪 Testing

This project uses **pytest** and **pytest-django**.

Run all tests:

```bash
pytest -q
```

---

# 📡 API Summary (High Level)

### Users

```http
POST /api/users/send-otp/
POST /api/users/verify-otp/
POST /api/users/token/
POST /api/users/token/refresh/
```

### Courses

```http
GET /api/courses/
GET /api/courses/<slug>/
GET /api/courses/categories/
GET /api/courses/instructors/
```

### Purchase

```http
GET  /api/purchase/cart/
POST /api/purchase/cart/add/
POST /api/purchase/apply-discount/
POST /api/purchase/checkout/
GET  /api/purchase/orders/
```

### Tickets

```http
GET  /api/tickets/tickets/
POST /api/tickets/tickets/
POST /api/tickets/tickets/reply/
```

### Admin Panel

```http
GET /api/admin-panel/users/
GET /api/admin-panel/orders/
GET /api/admin-panel/stats/
```

> For full details and all parameters, use the Postman collection.

---


# 🤝 Contributing

Contributions, issues, and feature requests are welcome.
Feel free to:

* Open an issue
* Submit a pull request

Please follow standard Django/DRF best practices and keep code well-documented.

---


# 📜 License

This project is licensed under the **MIT License**.

---


# 🧡 Credits

**Advance Kelaasor** is a product of the **Kelaasor** team.

Backend Development: **Taha Nasrollahi**

