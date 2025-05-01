FROM python:3.11-alpine
WORKDIR /app
EXPOSE 8000
ENV TZ=UTC
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=poetry.lock,target=poetry.lock \
    pip install pipx==1.7.1 \
    && pipx install --global poetry==1.8.3 \
    && poetry install --no-root --no-cache \
    && rm -rf ~/.cache/pypoetry \
    && rm -rf /opt/pipx
COPY . .
CMD ["python", "main.py"]
