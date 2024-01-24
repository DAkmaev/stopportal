FROM dakmaev/unicort-fastapi-poetry:latest

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

COPY ./ /app
ENV PYTHONPATH=/app

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
