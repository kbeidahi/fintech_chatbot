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

## LLM fallback

Undefined chat questions use Gemini after FAQ and action matching fails:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

If `GEMINI_API_KEY` is empty, the chatbot keeps the normal built-in fallback response.

An OpenAI-compatible provider can also be used as a secondary fallback. The default configuration targets OpenRouter with a free model:

```env
OPENAI_API_KEY=your_openrouter_api_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3.3-8b-instruct:free
```

If `OPENAI_API_KEY` is empty, only Gemini and the built-in fallback are used.

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
