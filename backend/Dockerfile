FROM python:3.11

WORKDIR /app/

COPY ./requirements.txt /app/
COPY ./alembic.ini /app/backend/
COPY ./app /app/backend/app

ENV PYTHONPATH=/app/

RUN pip install -r requirements.txt

CMD ["fastapi", "run", "backend/app/main.py", "--proxy-headers", "--port", "80"]
