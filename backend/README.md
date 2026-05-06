# Fintech Chatbot — Django Backend

## Stack
- Python 3.11+
- Django 4.2 + Django REST Framework
- PostgreSQL
- Redis (session caching)
- Simple JWT for authentication

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set env vars (see .env.example)
cp .env.example .env

python manage.py migrate
python manage.py seed_faq       # loads built-in FAQ data
python manage.py runserver
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/auth/register/ | Create account |
| POST | /api/auth/login/ | Get JWT tokens |
| POST | /api/auth/refresh/ | Refresh access token |
| POST | /api/chat/message/ | Send message, get reply |
| GET | /api/chat/sessions/ | List past sessions |
| GET | /api/chat/sessions/{id}/ | Session messages |
| GET | /api/faq/ | Browse FAQ categories |
