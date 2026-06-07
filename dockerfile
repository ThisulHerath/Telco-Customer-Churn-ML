# Multi-stage Dockerfile for production
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build deps for packages that need compilation
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into /install to copy into final image
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final minimal image
FROM python:3.11-slim

# Environment hardening
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Create unprivileged user
RUN addgroup --system app && adduser --system --ingroup app app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy only application code and exported serving bundle
COPY src src
COPY src/serving/model /app/src/serving/model

# Expose port used by FastAPI / Gunicorn
EXPOSE 8000

# Simple HTTP healthcheck using Python stdlib (exec form to avoid shell quoting)
HEALTHCHECK --interval=30s --timeout=3s CMD ["python", "-c", "import urllib.request,sys\ntry:\n    r=urllib.request.urlopen('http://localhost:8000/')\n    sys.exit(0 if r.getcode()==200 else 1)\nexcept Exception:\n    sys.exit(1)"]

# Run as unprivileged user
USER app

# Use Gunicorn with Uvicorn workers for production-grade serving
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.app.app:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
# 1. Use the official lightweight Python base image
FROM python:3.11-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy only dependency file first (for Docker caching)
COPY requirements.txt .

# 4. Install Python dependencies (add curl if you use MLflow local tracking URI)
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. Copy the entire project into the image
COPY . .

# Explicitly copy the exported serving bundle so inference.py can load it from /app/src/serving/model
COPY src/serving/model /app/src/serving/model

# make "serving" and "app" importable without the "src." prefix
# ensures logs are shown in real-time (no buffering).
# lets you import modules using from app... instead of from src.app....
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# 6. Expose FastAPI port
EXPOSE 8000

# 7. Run the FastAPI app using uvicorn (change path if needed)
CMD ["python", "-m", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]