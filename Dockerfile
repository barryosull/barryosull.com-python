# Multi-stage build: Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Accept build arguments for Vite environment variables
ARG VITE_API_URL
ARG VITE_WS_URL

# Set as environment variables for the build
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_WS_URL=${VITE_WS_URL}

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Main stage: Python application
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e .

# Copy frontend build artifacts from the frontend-builder stage
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Expose port for web app
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "src.adapters.api.main:app", "--host", "0.0.0.0", "--port", "8000"]