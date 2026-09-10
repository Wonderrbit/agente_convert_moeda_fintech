# CambioBot Dockerfile
# Multi-stage build for production

# =============================================================================
# Base Stage
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r cambiobot && useradd -r -g cambiobot cambiobot

# Set work directory
WORKDIR /app

# =============================================================================
# Dependencies Stage
# =============================================================================
FROM base as deps

# Install poetry for dependency management
RUN pip install --no-cache-dir poetry==1.8.2

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-interaction --no-ansi

# =============================================================================
# Development Stage
# =============================================================================
FROM deps as dev

# Install dev dependencies
RUN poetry install --with=dev,tradingagents --no-interaction --no-ansi

# Copy source code
COPY --chown=cambiobot:cambiobot . .

# Switch to non-root user
USER cambiobot

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "cambiobot.api.main"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Copy installed dependencies from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy source code
COPY --chown=cambiobot:cambiobot . .

# Switch to non-root user
USER cambiobot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "cambiobot.api.main"]