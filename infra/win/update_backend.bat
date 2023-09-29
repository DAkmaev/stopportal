cd ..\..\..\
git pull
venv\Scripts\activate
cd stopportal\backend
poetry install
alembic upgrade "head"
poetry run python -m backend