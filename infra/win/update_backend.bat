cd ..\..\
git pull
cd ..\
venv\Scripts\activate
cd stopportal\backend
poetry install
alembic upgrade "head"
poetry run python -m backend
