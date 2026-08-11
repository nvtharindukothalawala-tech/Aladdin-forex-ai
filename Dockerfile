FROM python:3.14-slim

WORKDIR /app

# ==========================================
# Python production settings
# ==========================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ==========================================
# System dependencies
# ==========================================

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Python dependencies
# ==========================================

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# ==========================================
# Application source
# ==========================================

COPY . .

# ==========================================
# Non-root application user
# ==========================================

RUN useradd --create-home --shell /bin/bash aladdin \
    && chown -R aladdin:aladdin /app

USER aladdin

# ==========================================
# Application port
# ==========================================

EXPOSE 8000

# ==========================================
# Start FastAPI
# ==========================================

CMD [
    "uvicorn",
    "app.api.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]