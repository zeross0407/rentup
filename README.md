# RentUp Backend

FastAPI backend for the RentUp rental platform.

## Tech Stack

- **Framework**: FastAPI 0.128.8
- **Language**: Python 3.9+
- **Database**: MongoDB Atlas (async via Motor)
- **ODM**: Beanie (Pydantic-based ODM)
- **Auth**: JWT (python-jose) + bcrypt (passlib)

## Getting Started

### 1. Setup virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your MongoDB Atlas connection string
```

### 4. Run development server

```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py              # Application entry point
├── core/                # Core configuration & utilities
│   ├── config.py        # Settings management
│   ├── database.py      # MongoDB connection (Motor + Beanie)
│   ├── security.py      # JWT & password utilities
│   ├── dependencies.py  # Shared dependencies
│   └── exceptions.py    # Custom exception handlers
├── models/              # Beanie document base
├── schemas/             # Pydantic response schemas
└── modules/             # Feature modules
    └── users/           # User module (auth, profile)
```
# rentup
