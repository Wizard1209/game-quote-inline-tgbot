FROM python:3.12-alpine

WORKDIR /app
RUN useradd -m app && chown -R app:app /app
USER app

COPY pyproject.toml /app/.
RUN pip install .

CMD ["python", "src/app.py", "/app/api_key.txt"]