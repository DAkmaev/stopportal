#!/bin/bash

environment=$1

if [[ -n "$environment" ]]; then
    echo "Backup $environment DB"
else
    echo "No set environment"
fi

# Load environment variables from .env file
set -a
source .env
set +a

docker compose -f docker-compose-prod.yml -p prod exec db pg_dump -d "postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}" > backup_"$environment".sql
