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

## Before opening a pull request

```bash
pytest           # all tests pass
ruff check .     # no lint errors
ruff format .    # consistent formatting
```

## Layout

Matches the component diagram.

```
backend/
├── app/
│   ├── main.py          # creates the app and registers the routers
│   ├── core/            # settings shared across the app
│   ├── routers/         # one file per feature: health now; auth, buses, journeys, tracking, boarding, notifications, reports later
│   ├── models/          # SQLAlchemy database models (issue #7)
│   ├── schemas/         # Pydantic request and response models
│   └── services/        # ETA, arrival detection, boarding window
├── tests/               # pytest
├── requirements.txt     # packages needed to run
└── requirements-dev.txt # extra tools for development and testing
```
Each folder has an empty `__init__.py` so Python treats it as a package.