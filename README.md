# 🚀 Advanced E-commerce Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.0-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.35-red?style=flat-square)](https://www.sqlalchemy.org/)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-blueviolet?style=flat-square&logo=stripe&logoColor=white)](https://stripe.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A robust, production-ready e-commerce backend built with **FastAPI**, featuring a modular architecture, asynchronous database operations, and integrated payment/tracking systems.

---

## ✨ Key Features

- 🔐 **Authentication & Authorization**: Secure JWT-based authentication with password hashing (Bcrypt).
- 🛒 **Cart Management**: Persistent shopping carts with stock validation and real-time updates.
- 💳 **Payment Integration**: Seamless Stripe Checkout integration for secure transactions.
- 📦 **Order Management**: Comprehensive order lifecycle from creation to delivery.
- 🚚 **Shipment Tracking**: Real-time shipment status updates and timeline tracking for users and admins.
- 📧 **Automated Emails**: Beautiful HTML email notifications for order confirmation and admin alerts.
- 📊 **Robust Database**: PostgreSQL with SQLAlchemy (Async) and Alembic for schema migrations.
- 🛡️ **Standardized API**: Consistent response structures and global exception handling.

---

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Async via `asyncpg`)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Security**: [Jose (JWT)](https://python-jose.readthedocs.io/), [Passlib (Bcrypt)](https://passlib.readthedocs.io/)
- **Payments**: [Stripe Python SDK](https://stripe.com/docs/libraries/python)
- **Emails**: [FastAPI-Mail](https://github.com/sabuhish/fastapi-mail)
- **Logging**: Structured logging for observability.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- PostgreSQL
- Stripe Account (for payments)

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone <repository-url>
cd ecommerce-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory based on `.env.example`:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=ecommerce_db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Stripe
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Database Migrations
Run the migrations to set up your database schema:

```bash
alembic upgrade head
```

### 5. Running the Application
Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the interactive documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📂 Project Structure

```text
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API versioning (v1)
│   ├── core/             # Config, Security, Logging, Exceptions
│   ├── db/               # Session management, Base models
│   ├── models/           # SQLAlchemy models
│   ├── routers/          # API endpoints (Auth, Products, Cart, Orders, etc.)
│   ├── schemas/          # Pydantic models (Request/Response)
│   ├── services/         # Business logic (Stripe, Email, Tracking)
│   ├── templates/        # HTML templates for emails
│   └── main.py           # Application entry point
├── .env                  # Environment secrets
├── requirements.txt      # Project dependencies
└── alembic.ini           # Alembic configuration
```

---

## 📡 API Endpoints

| Category | Endpoint | Description |
| :--- | :--- | :--- |
| **Auth** | `POST /api/v1/auth/login` | Login and get JWT token |
| **Users** | `POST /api/v1/users/` | Register a new user |
| **Products** | `GET /api/v1/products/` | List all products |
| **Cart** | `POST /api/v1/cart/` | Add item to cart |
| **Orders** | `POST /api/v1/orders/` | Create an order / Stripe Checkout |
| **Tracking** | `GET /api/v1/orders/{order_id}/tracking` | Track order status |

---

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
