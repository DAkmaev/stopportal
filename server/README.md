# server

## Local debug
Create Virtual env and install requirements.
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Rum server dev
```bash
fastapi dev src/main.py
```

Run server prod
```bash
fastapi prod src/main.py
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
