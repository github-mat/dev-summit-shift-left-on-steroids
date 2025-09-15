FROM python:3.11-slim

# Install system dependencies for WeasyPrint (Cairo, Pango, GDK-Pixbuf, libffi, libgobject)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency configuration files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using UV (production only)
RUN uv sync --no-dev

# Copy application source code
COPY src/ ./

# Use UV to run the application
CMD ["uv", "run", "python", "app.py"]