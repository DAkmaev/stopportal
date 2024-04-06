FROM python:3.11

WORKDIR /app/

RUN pip install poetry alembic pydantic-settings

COPY ./app /app/app
COPY ./pyproject.toml /app/

ENV PYTHONPATH=/app/

RUN poetry install

#ENTRYPOINT bash
CMD ["poetry", "run", "uvicorn", "app.web.application:get_app", "--host", "0.0.0.0", "--port", "80"]
