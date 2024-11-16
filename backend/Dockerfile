FROM python:3.11

WORKDIR /app/backend/

COPY ./requirements.txt /app/backend
COPY ./alembic.ini /app/backend
COPY ./app /app/backend/app

ENV PYTHONPATH=/app/backend/

RUN pip install -r requirements.txt

CMD ["fastapi", "prod", "app/main.py"]
