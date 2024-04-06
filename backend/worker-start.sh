#! /usr/bin/env bash
set -e

poetry run celery -A app.worker worker --loglevel=info  --pool solo
