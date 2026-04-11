FROM python:3.12-slim

# System deps for scientific packages (libgomp1 for scikit-learn/OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Non-root user with configurable UID (match host UID on Linux)
ARG UID=1000
RUN useradd -m -u ${UID} developer
USER developer
WORKDIR /workspace

# Dependency layer caching: copy metadata + minimal source first
COPY --chown=developer:developer pyproject.toml uv.lock .python-version ./
COPY --chown=developer:developer src/auto_alpha_miner/__init__.py ./src/auto_alpha_miner/__init__.py
RUN uv sync --frozen --group dev

# NOTE: At runtime, source is bind-mounted via docker-compose.yml.
# postCreateCommand runs `uv sync` to install the project in editable mode.

CMD ["bash"]
