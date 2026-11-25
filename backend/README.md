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
Add a `SECRET_KEY` to `.env` (it signs sign-in tokens; never commit it):

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Create an account to sign in with (it asks for the password without showing it):

```bash
python -m app.create_user --name "Test Student" --email student@alustudent.com --role student
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
## The route along the real roads (#79)

The map draws the road path saved in `app/data/road_path.json`. To fetch it (once, needs internet):

```bash
python -m app.road_path
```

It prints any stop more than 60 m from the path. If the engine took a different road there, add a
point the bus really passes to `VIA_POINTS` in `app/road_path.py` and run it again. Without the
file, the map joins the stops with straight lines.
