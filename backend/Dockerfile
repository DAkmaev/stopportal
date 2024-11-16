FROM python:3.11

WORKDIR /app/backend/

COPY ./requirements.txt /app/server
COPY ./alembic.ini /app/backend
COPY ./src /app/backend/app

ENV PYTHONPATH=/app/backend/

RUN pip install -r requirements.txt

CMD ["fastapi", "prod", "app/main.py"]
