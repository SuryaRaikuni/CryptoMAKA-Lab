# Backend Dockerfile for CryptoMAKA Lab
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY backend/ backend/

# Install the package in editable mode with production dependencies
RUN pip install --no-cache-dir build && \
    pip install --no-cache-dir -e .

# --- Runner stage ---
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment/installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/backend /app/backend

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DATABASE_URL=sqlite:///./data/cryptomaka_prod.db

# Create data directory for SQLite if PostgreSQL isn't used
RUN mkdir -p /app/data && chown -R 1000:1000 /app/data

# Switch to non-root user
USER 1000:1000

# Expose port
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "cryptomaka.main:app", "--host", "0.0.0.0", "--port", "8000"]
