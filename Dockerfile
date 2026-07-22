FROM python:3.12-slim

# uv gives fast, reliable installs straight from pyproject.toml
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency manifests first so Docker can cache this layer
# separately from your application code. Copying uv.lock alongside
# pyproject.toml lets us install the exact versions resolved and
# tested locally, rather than re-resolving fresh at build time.
COPY pyproject.toml uv.lock ./

# --no-install-project: only install the dependencies listed in
# pyproject.toml — we don't need this project packaged/installed itself,
# just its deps available to run main.py directly.
# --frozen: fail the build instead of silently re-resolving if uv.lock
# and pyproject.toml ever drift out of sync.
RUN uv sync --no-install-project --frozen

# Now copy the actual application code and model artifacts.
COPY main.py ./
COPY app ./app
COPY model ./model

ENV PATH="/app/.venv/bin:$PATH"

# Render (and most PaaS platforms) inject $PORT at runtime — bind to it,
# don't hardcode 8000.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]