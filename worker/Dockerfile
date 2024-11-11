FROM python:3.11

WORKDIR /app/


COPY ./requirements.txt /app/

COPY ./src /app/worker/src
ENV PYTHONPATH=/app/

RUN pip install -r requirements.txt

CMD ["celery", "-A", "worker.src.tasks", "worker", "--loglevel=info"]
