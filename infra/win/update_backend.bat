cd ..\..\
git pull
cd ..\
call venv\Scripts\activate
cd stopportal\backend
poetry install
alembic upgrade "head"
