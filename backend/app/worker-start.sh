#! /usr/bin/env bash
set -e

celery -A app.worker worker --loglevel=info
