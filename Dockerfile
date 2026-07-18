# syntax=docker/dockerfile:1

# ---------- Build stage ----------
FROM python:3.12-slim-trixie AS builder

COPY --from=ghcr.io/astral-sh/uv:0.8.21 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# Install deps first, separate from app code, for better layer caching
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

COPY app/ ./app/
COPY model/ ./model/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ---------- Runtime stage ----------
FROM python:3.12-slim-trixie AS runtime

# xgboost needs libgomp at runtime (OpenMP) — without this the build succeeds
# but the app crashes with an ImportError the moment it tries to load the model
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1001 appgroup \
    && useradd -u 1001 -g appgroup -m -d /home/appuser -s /bin/false appuser

WORKDIR /app
COPY --from=builder --chown=appuser:appgroup /app /app

ENV PATH="/app/.venv/bin:$PATH"
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
