# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder
WORKDIR /app
COPY ../../pyproject.toml ./
RUN pip install --upgrade pip && \
    python - <<'PY'
import pathlib, tomllib
pyproject = tomllib.loads(pathlib.Path('pyproject.toml').read_text())
deps = pyproject['project']['dependencies']
pathlib.Path('requirements.txt').write_text('\n'.join(deps))
PY
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY ../../shared ./shared
COPY . .
ENV DJANGO_SETTINGS_MODULE=dashboard.settings
RUN useradd -m appuser
USER appuser
CMD ["gunicorn", "dashboard.wsgi:application", "-b", "0.0.0.0:8001", "-k", "uvicorn.workers.UvicornWorker"]
