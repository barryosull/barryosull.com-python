# barryosull.com-python
My personal site and blog in Python.

## Local Development

### Setup
```bash
# Install dependencies
pip install -e ".[dev]"

# Run CLI
my-app hello World

# Run web server
my-app-web

# Run tests
pytest
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
