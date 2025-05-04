FROM python:3.13-slim-bookworm as build

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

WORKDIR /opt/app

COPY pyproject.toml ./
COPY uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# Create image with compiled dependencies and no dev dependencies or uv
FROM python:3.13-slim-bookworm as production

COPY --from=build /opt/app/.venv /opt/app/.venv

WORKDIR /opt/app

COPY sastb ./sastb

RUN mkdir -p ./db

ENV PYTHONPATH "${PYTHONPATH}:/opt/app"
ENV PATH "/opt/app/.venv/bin:${PATH}"

EXPOSE 8080

ENTRYPOINT ["python", "-m", "sastb", "start"]
