# Avomd GPT Job Backend

This project is a minimal async backend API for guideline ingestion and checklist generation using OpenAI GPT, built with Django, Celery, Redis, and Postgres.

## Features
- **POST /jobs**: Queue a text for processing, returns an event_id in <200ms.
- **GET /jobs/{event_id}**: Check job status and result (summary + checklist).
- **Async processing**: Celery worker runs a two-step GPT chain (summarize → checklist).
- **OpenAPI/Swagger**: Auto-generated API docs at `/swagger/`, `/redoc/`, `/schema/`.
- **Test coverage**: Unit tests for API and Celery logic, ~70%+ coverage.

## How to Run
1. Clone the repo.
2. Add your OpenAI API key to `.env` (never commit secrets!).
3. Run:
   ```bash
   docker compose up --build
   ```
4. Access API docs at [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

## How to Test
- To run all tests:
  ```bash
  pytest
  ```
- To check test coverage:
  ```bash
  pytest --cov=job --cov-report=term-missing
  ```

## Design & AI Tools
- All async logic is handled via Celery + Redis for true background processing.
- Job status/results are persisted in Postgres.
- Used AI tools (Cursor, Copilot) for rapid code scaffolding, test generation, and OpenAPI integration. 

Name                             Stmts   Miss  Cover
----------------------------------------------------
config/__init__.py                   0      0   100%
config/settings.py                  24      0   100%
config/urls.py                       3      0   100%
job/__init__.py                      0      0   100%
job/admin.py                         1      0   100%
job/apps.py                          4      0   100%
job/migrations/0001_initial.py       6      0   100%
job/migrations/__init__.py           0      0   100%
job/models.py                        8      0   100%
job/serializers.py                  12      0   100%
job/tasks.py                        21      3    86%
job/tests.py                        61      0   100%
job/urls.py                          3      0   100%
job/views.py                        26      0   100%
----------------------------------------------------
TOTAL                              169      3    98%