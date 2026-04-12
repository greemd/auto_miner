FROM python:3.12-slim

# System deps for scientific packages (libgomp1 for scikit-learn/OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Node.js (required for Claude Code CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Non-root user with configurable UID (match host UID on Linux)
ARG UID=1000
RUN useradd -m -u ${UID} developer
USER developer
WORKDIR /workspace

# Dependency layer caching: copy metadata + minimal source first
COPY --chown=developer:developer pyproject.toml uv.lock ./
COPY --chown=developer:developer src/auto_alpha_miner/__init__.py ./src/auto_alpha_miner/__init__.py
RUN uv sync --frozen --group dev

# At runtime, source is bind-mounted via docker-compose.yml.
# Run `uv sync --group dev` inside the container to install in editable mode.

CMD ["bash"]
