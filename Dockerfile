FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# (Optional) system build deps; remove if not needed
RUN apt-get update && apt-get install -y --no-install-recommends build-essential  \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create venv to copy into runtime image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Leverage Docker layer caching for dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

############################
# Runtime
############################
FROM python:3.12-slim AS runtime

# Minimal runtime tools (uncomment curl if you want HTTP healthchecks in compose)
# RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Non-root user
RUN adduser --disabled-password --gecos "" app && chown -R app:app /app
USER app

# Bring in the prebuilt venv and the app code
COPY --from=builder /opt/venv /opt/venv
COPY ./src /app

EXPOSE 8000

CMD ["python", "main.py"]