FROM python:3.11

WORKDIR /app/

RUN pip install poetry alembic pydantic-settings yarl aiosqlite psycopg


### Copy poetry.lock* in case it doesn't exist in the repo
#COPY ./pyproject.toml ./poetry.lock /app

#COPY ./app/ /app
COPY ./ /app
ENV PYTHONPATH=/app

RUN poetry install

CMD ["poetry", "run", "uvicorn", "app.web.application:get_app", "--host", "0.0.0.0", "--port", "80"]
