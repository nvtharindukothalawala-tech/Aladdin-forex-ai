FROM python:3.14-slim


WORKDIR /app


# Python production settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install curl for Docker healthcheck
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Copy application source
COPY . .


# Create non-root application user
RUN useradd -m aladdin


# Change ownership
RUN chown -R aladdin:aladdin /app


# Run container as non-root user
USER aladdin


EXPOSE 8000


CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]