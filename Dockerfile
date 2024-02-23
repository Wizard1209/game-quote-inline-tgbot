FROM python:3.12-alpine

WORKDIR /app
RUN adduser -D app && chown -R app:app /app
USER app

COPY pyproject.toml /app/.
RUN pip install .

CMD ["python", "src/app.py"]