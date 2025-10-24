# Secret Hitler - Online Game

Online implementation of the Secret Hitler board game using Python and FastAPI.

Rules can be found here: https://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf

## Quick Start (Docker - Recommended)

The easiest way to run the application is using Docker Compose:

```bash
# Start the application (development mode with live reload)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

The application will be available at:
- **Frontend Dev Server** (with hot reload): http://localhost:3001
- **Production Build** (via nginx): http://localhost:8080
- **API**: http://localhost:8080/api
- **API Documentation**: http://localhost:8080/docs

> **💡 Development Tip:** Use http://localhost:3001 for frontend development (instant hot reload). Changes to backend code (`src/`) automatically reload the server.

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development workflows.

### Architecture

The Docker setup includes:
- **Nginx** (port 8080) - Reverse proxy with gzip compression
- **FastAPI Backend** (internal port 8000) - Python API server
- **React Frontend** - Single-page application served by nginx
- **SQLite Database** - Persisted in `./data/` directory

### Database Persistence

Game data is stored in `./data/db.sqlite` on your host machine, so it persists between container restarts.

## Local Development

For active development without Docker:

### Backend Setup
```bash
# Create virtual environment
python3 -m venv venv

# Install dependencies
./venv/bin/pip install -e ".[dev]"

# Run tests
./venv/bin/pytest tests/ -v

# Run tests with coverage
./venv/bin/pytest tests/ --cov=src --cov-report=html

# Run web server
./venv/bin/python -m uvicorn src.adapters.api.main:app --port=8000 --reload

# Format code
./venv/bin/black src/ tests/

# Lint code
./venv/bin/ruff check src/ tests/

# Type check
./venv/bin/mypy src/
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The frontend dev server will run on http://localhost:3000

See [frontend/README.md](frontend/README.md) for more frontend development details.
