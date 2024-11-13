FROM python:3.11

WORKDIR /app/server/

COPY ./requirements.txt /app/server
COPY ./alembic.ini /app/server
COPY ./src /app/server/src

ENV PYTHONPATH=/app/server/

RUN pip install -r requirements.txt

CMD ["fastapi", "prod", "src/main.py"]
