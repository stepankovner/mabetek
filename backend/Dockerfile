FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .
RUN useradd --uid 10001 --create-home app
USER app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*"]
