# Development Guide

## Architecture Overview

The project uses a dual Docker Compose setup:

- **`docker-compose.yml`** - Production configuration
- **`docker-compose.override.yml`** - Development overrides (auto-loaded)
    - This file is excluded by .gitignore so that it isn't loaded in prod
    - Local copy must be created first (copy example version) for dev overrides to work

## Development Mode

When you run `docker-compose up -d`, both files are automatically merged, giving you:

### Backend (FastAPI)
- ✅ **Live reload** - Changes to `src/` automatically restart the server
- ✅ **Volume mounted** - Edits reflected immediately
- ✅ **Accessible via nginx** - http://localhost:8080/api

### Frontend (React + Vite)
- ✅ **Hot module reload** - Instant updates without page refresh
- ✅ **Dev server** - Running on http://localhost:3000
- ✅ **Source maps** - Full debugging support

### Database
- ✅ **Persisted** - Data stored in `./data/db.sqlite`

## Quick Start

```bash

# Create a version of the override file that is automatically loaded
cp docker-compose.override.example.yml docker-compose.override.yml

# Start everything in development mode
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app          # Backend
docker-compose logs -f frontend-dev # Frontend

# Restart a service after config changes
docker-compose restart app

# Stop everything
docker-compose down
```

## Access URLs

During development:
- **Frontend Dev Server**: http://localhost:3001 (with hot reload)
- **Production Build**: http://localhost:8080 (via nginx)
- **API**: http://localhost:8080/api (via nginx)
- **API Docs**: http://localhost:8080/docs
- **Multi-Player Test**: http://localhost:3001/test-multi-player.html

## Making Changes

### Backend Changes
1. Edit files in `src/`
2. Save - uvicorn auto-reloads
3. Check logs: `docker-compose logs -f app`

### Frontend Changes
1. Edit files in `frontend/src/`
2. Save - Vite hot-reloads automatically
3. Changes appear instantly in browser at http://localhost:3000

### Configuration Changes
If you modify `docker-compose.yml` or `Dockerfile`:
```bash
docker-compose up -d --build
```

## Production Build

To test the production build locally:

```bash
# Temporarily rename override file
mv docker-compose.override.yml docker-compose.override.yml.bak

# Build and run production setup
docker-compose up -d --build

# Access at http://localhost:8080

# Restore development setup
mv docker-compose.override.yml.bak docker-compose.override.yml
docker-compose up -d
```

## Troubleshooting

### Frontend not updating?
```bash
# Rebuild frontend service
docker-compose restart frontend-dev

# Or rebuild from scratch
docker-compose up -d --build frontend-dev
```

### Backend not reloading?
```bash
# Check if volume is mounted correctly
docker-compose exec app ls -la /app/src

# Restart the service
docker-compose restart app
```

### Port conflicts?
If port 3001 or 8080 are in use:
```bash
# Edit docker-compose.override.yml and change the ports
# Frontend: "3002:3000"  # Change host port
# Nginx: "8081:80"       # Change nginx port in docker-compose.yml
```

## Running Tests

```bash
# Backend tests
docker-compose exec app pytest tests/ -v

# Or locally with venv
./venv/bin/pytest tests/ -v
```

## Tips

1. **Use frontend dev server** (http://localhost:3000) for development - it's faster with HMR
2. **Use production build** (http://localhost:8080) to test nginx, compression, and production features
3. **Backend always uses hot reload** in development mode
4. **Database persists** - your game data survives restarts
