# Backend

## Local debug
Create Virtual env and install requirements.
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Rum backend dev
```bash
fastapi dev app/main.py
```

Run backend prod
```bash
fastapi prod app/main.py
```


## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```

## Worker

### Local start
```bash
cd ../
celery -A  backend.app.worker.tasks worker --loglevel=info
or
celery -A  backend.app.worker.tasks --loglevel=info -Q run_calculation,ta_calculation,ta_final
```
