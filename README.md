# Django REST Framework (DRF) Project

A comprehensive Django REST Framework application with subscription management, including a 30-day free trial feature using Razorpay.

## Features

- Custom User model with email authentication
- JWT Authentication using Simple JWT
- API documentation with Swagger/ReDoc
- Subscription management with Razorpay integration
- 30-day free trial implementation
- Background tasks using Celery and Redis
- PostgreSQL database integration
- Environment variable management with python-dotenv

## Project Structure

```
drf/
├── apps/                    # Application modules
│   ├── api/                 # API endpoints and serializers
│   ├── common/              # Shared functionality and models
│   └── users/               # User management
├── core/                    # Project settings and configuration
├── logs/                    # Application logs
├── media/                   # User uploaded files
├── static/                  # Static files
├── venv/                    # Virtual environment
├── .env                     # Environment variables
├── manage.py                # Django management script
└── README.md                # Project documentation
```

## Prerequisites

- Python 3.13
- PostgreSQL 16.3
- Redis (for Celery)

## Setup Instructions

1. **Clone the repository**

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` and update the values
   - Set your database credentials
   - Add Razorpay API keys if needed

5. **Create PostgreSQL database**
   ```bash
   createdb test
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Start Celery worker (in a separate terminal)**
   ```bash
   celery -A core worker -l info
   ```

10. **Start Celery beat for scheduled tasks (in a separate terminal)**
    ```bash
    celery -A core beat -l info
    ```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Subscription Management

The application includes a complete subscription management system with:

- 30-day free trial for new users
- Automatic billing after trial expiration
- Trial cancellation up to 24 hours before expiration
- Daily background job to check for trial expirations

## Testing

Run tests with:

```bash
pytest
```

## Frontend Integration

This backend is designed to work with a Next.js frontend (to be implemented separately). The API endpoints are structured to support a modern frontend application.

## License

This project is licensed under the MIT License.
