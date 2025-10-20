# Secret Hitler - Online Game

Online implementation of the Secret Hitler board game using Python and FastAPI.

Rules can be found here: https://www.secrethitler.com/assets/Secret_Hitler_Rules.pdf

## Local Development

### Setup
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

## Docker

### Build and Run
```bash
# Build the Docker image
docker build -t barryosull-app .

# Run the web server
docker run -p 8000:8000 barryosull-app

# Run CLI commands
docker run barryosull-app my-app hello World

# Run with environment variables
docker run -e DEBUG=true -p 8000:8000 barryosull-app
```

### Docker Compose (optional)
```bash
docker-compose up
```

The web app will be available at http://localhost:8000
