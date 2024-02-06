#!/bin/bash

# Load environment variables from .env file
set -a
source .env
set +a

# Backup database
pg_dump -U "$POSTGRES_USER" -h "$POSTGRES_SERVER" -d "$POSTGRES_DB" > /db_backup/backup.sql

# Apply migrations
alembic upgrade head
