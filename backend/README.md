# Backend

FastAPI service for ALU SmartBus: REST API, WebSockets for live tracking, and the business logic (ETA, arrival detection, boarding window, QR validation).

## Run it locally

Needs Python 3.11 or newer.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then open http://localhost:8000/health (should show `{"status": "ok"}`) or http://localhost:8000/docs for the interactive API docs.

## Database (first time)

The backend uses PostgreSQL. For local development it runs in Docker.

```bash
# from the project root: start the database
docker compose up -d

# from backend/: create your settings file, then the tables
cp .env.example .env
alembic upgrade head

# add the Rebero - ALU route and its stops
python -m app.seed
```

`python -m app.seed` refuses to run until every stop in `app/seed_data.py` has real coordinates.

After changing a model, create and apply a migration:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Before opening a pull request

```bash
pytest           # all tests pass
ruff format .    # consistent formatting
ruff check .     # no lint errors
```

## Layout

Matches the component diagram.

```
backend/
├── app/
│   ├── main.py          # creates the app and registers the routers
│   ├── db.py            # database connection and the base class for models
│   ├── seed.py          # adds the route and stops (python -m app.seed)
│   ├── seed_data.py     # the route's stops and their coordinates
│   ├── core/            # settings read from .env (config.py)
│   ├── routers/         # one file per feature: health now; auth, buses, journeys, tracking, boarding, notifications, reports later
│   ├── models/          # database tables, one file per area (users, buses, routes, journeys, student activity)
│   ├── schemas/         # Pydantic request and response models
│   └── services/        # ETA, arrival detection, boarding window
├── alembic/             # migrations: numbered changes to the database
├── tests/               # pytest
├── .env.example         # settings to copy into .env (never commit .env)
├── requirements.txt     # packages needed to run
└── requirements-dev.txt # extra tools for development and testing
```

Each folder has an empty `__init__.py` so Python treats it as a package.