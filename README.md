# Advance Kelaasor API

A production-grade Django REST Framework backend for an online learning platform (bootcamps, online/offline courses). Built as part of the Kelaasor ecosystem.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Django 5.2.7 |
| API Toolkit | Django REST Framework 3.16.1 |
| Authentication | SimpleJWT (OTP + Password-based JWT) |
| Task Queue | Celery 5.5.3 |
| Message Broker | Redis 7.1.0 |
| Database | PostgreSQL (psycopg2-binary 2.9.11) |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-django |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT (Mobile/Web)              │
│              Authorization: Bearer <JWT>            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Django REST Framework                   │
│    Authentication · Permissions · Throttling         │
└──────┬───────────────┬──────────────┬───────────────┘
       │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌────▼──────────────┐
│   Serializers│ │   Services  │ │Custom Permissions  │
│  (input/     │ │ (OTP,       │ │(7 classes +        │
│   output)    │ │  checkout)  │ │ 6 admin RBAC)      │
└──────┬──────┘ └──────┬──────┘ └───────────────────┘
       │               │
┌──────▼──────┐ ┌──────▼──────┐
│   Models    │ │   Redis     │
│  (23 total) │ │  (OTP codes)│
└──────┬──────┘ └─────────────┘
       │
┌──────▼──────────────────────────┐
│  PostgreSQL Database            │
│  6 apps, 23 models             │
└─────────────────────────────────┘

Background:
┌──────────────┐    ┌──────────────┐
│ Celery Beat  │───▶│ Celery Worker │
│ (price task) │    │ (autodiscover)│
└──────────────┘    └───────┬──────┘
                            │
                    ┌───────▼──────┐
                    │  Redis       │
                    │  (broker)    │
                    └──────────────┘
```

## Features

- **Mobile OTP Authentication** - Send OTP via SMS, verify to receive JWT tokens
- **JWT Token Management** - Access/refresh tokens with blacklisting support
- **Course Catalog** - Hierarchical categories, instructor profiles, chapters, videos, attachments
- **E-Commerce** - Cart → Checkout → Order → Payment → Enrollment flow
- **Discount Codes** - Percent/fixed discounts with user/course scoping and usage limits
- **Support Ticketing** - Threaded messages with email notifications
- **User Dashboard** - Aggregated view of orders, tickets, and announcements
- **Admin Panel** - Role-based access (Admin, Support, ProductManager, Instructor)
- **Dynamic Pricing** - Celery Beat task increases online course prices near deadline
- **Soft Delete** - User accounts soft-deleted to preserve data integrity

## API Overview

| Module | Base Path | Endpoints | Description |
|--------|-----------|-----------|-------------|
| Users | `/api/users/` | 8 | Auth, OTP, JWT, password reset |
| Courses | `/api/courses/` | 9 | Categories, instructors, courses, videos |
| Purchase | `/api/purchase/` | 6 | Cart, checkout, orders, discounts |
| Tickets | `/api/tickets/` | 3 | Support ticket CRUD + replies |
| Admin Panel | `/api/admin-panel/` | 13 | User/order/ticket/discount management |
| User Panel | `/api/user_panel/` | 1 | Dashboard aggregation |

**Total: 40 API endpoints**

## Authentication System

### OTP Flow
1. `POST /api/users/send-otp/` → Send 6-digit code to mobile (stored in Redis, 5-min TTL)
2. `POST /api/users/verify-otp/` → Verify code → receive JWT access/refresh tokens

### Password Flow
1. `POST /api/users/token/` → Login with mobile + password → receive JWT tokens
2. `POST /api/users/token/refresh/` → Refresh expired access token

### Logout
- `POST /api/users/token/blacklist/` → Blacklist refresh token

### Password Reset
1. `POST /api/users/password/forgot/` → Send reset OTP
2. `POST /api/users/password/reset/` → Verify OTP + set new password

## Installation

### Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd kelaasor_advance

# 2. Create environment file
cp .env.example .env
# Edit .env with your secrets

# 3. Build and start services
docker-compose up -d --build

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create environment file
cp .env.example .env
# Edit .env with your local configuration

# 4. Start PostgreSQL and Redis
# (Use Docker or local installation)

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver

# 8. Start Celery worker (in separate terminal)
celery -A kelaasor_advance worker --loglevel=info

# 9. Start Celery beat (in separate terminal)
celery -A kelaasor_advance beat --loglevel=info
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key |
| `DEBUG` | No | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | Yes | - | Comma-separated allowed hosts |
| `DB_NAME` | Yes | - | PostgreSQL database name |
| `DB_USER` | Yes | - | PostgreSQL user |
| `DB_PASSWORD` | Yes | - | PostgreSQL password |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `CELERY_BROKER_URL` | Yes | - | Redis URL for Celery broker |
| `CELERY_RESULT_BACKEND` | Yes | - | Redis URL for Celery results |
| `CORS_ALLOWED_ORIGINS` | Yes | - | Comma-separated allowed origins |
| `EMAIL_HOST_USER` | No | - | SMTP email username |
| `EMAIL_HOST_PASSWORD` | No | - | SMTP email password |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | No | `30` | JWT access token lifetime |
| `REFRESH_TOKEN_LIFETIME_DAYS` | No | `7` | JWT refresh token lifetime |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific app tests
pytest tests/users/
pytest tests/courses/
pytest tests/purchase/
```

## Project Structure

```
kelaasor_advance/
├── kelaasor_advance/     # Project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # Root URL configuration
│   ├── celery.py         # Celery configuration
│   └── wsgi.py           # WSGI entry point
├── users/                # Authentication & user management
│   ├── models.py         # User, UserProfile, TeamEnrollment, Announcement
│   ├── views.py          # Auth views (OTP, JWT, register)
│   ├── serializers.py    # Auth serializers
│   ├── services/         # OTP service (Redis-backed)
│   ├── permissions.py    # Custom permissions
│   └── throttles.py      # Rate limiting
├── courses/              # Course catalog
│   ├── models.py         # Category, Instructor, Course, Chapter, Video, Attachment
│   ├── views.py          # Read-only course views
│   ├── tasks.py          # Celery task (dynamic pricing)
│   └── permissions.py    # Enrollment-based video access
├── purchase/             # E-commerce
│   ├── models.py         # Order, OrderItem, Participant, Enrollment, Payment, DiscountCode
│   ├── views.py          # Cart, checkout, orders, discounts
│   └── services/         # Checkout service (atomic operations)
├── ticket/               # Support ticketing
│   ├── models.py         # Ticket, TicketMessage
│   ├── views.py          # Ticket CRUD + replies
│   └── utils.py          # Email/SMS notification helpers
├── admin_panel/          # Admin management
│   ├── views/            # User, order, ticket, discount, notification management
│   ├── serializers/      # Admin-specific serializers
│   └── permissions.py    # Role-based access (6 classes)
├── user_panel/           # User dashboard
│   └── views.py          # Aggregated dashboard endpoint
├── tests/                # Test suite
│   ├── conftest.py       # Shared fixtures
│   └── */                # App-specific tests
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Full stack orchestration
├── requirements.txt      # Python dependencies
└── manage.py             # Django management script
```

## Deployment

### Docker Compose Services

| Service | Description | Port |
|---------|-------------|------|
| `web` | Django API (gunicorn) | 8000 |
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |
| `celery_worker` | Celery task worker | - |
| `celery_beat` | Celery task scheduler | - |

### Production Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Scale workers
docker-compose up -d --scale celery_worker=4
```

## Developer Notes

- **OTP Storage**: OTP codes are stored in Redis with 5-minute TTL. The OTP service uses `hmac.compare_digest` for constant-time comparison.
- **Checkout Flow**: Uses `select_for_update()` and `@transaction.atomic` for safe concurrent checkout operations.
- **Soft Delete**: User deletion sets `deleted=True` and `is_active=False` instead of hard delete.
- **JWT Blacklisting**: Token rotation is enabled. Refresh tokens are blacklisted after use.
- **CORS**: Configured via `CORS_ALLOWED_ORIGINS` environment variable.
- **Security Headers**: HSTS, secure cookies, XSS filter, and content type nosniff are enabled in production.
- **Logging**: Structured logging to console and files (`logs/django.log`, `logs/errors.log`).

## License

Proprietary - Kelaasor
