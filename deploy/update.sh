#!/bin/bash

environment=$1
branch="deploy"

if [[ -n "$environment" ]]; then
    echo "Environment $environment"
else
    echo "No set environment"
fi



# Download required files from GitHub
curl -O https://raw.githubusercontent.com/DAkmaev/stopportal/$branch/deploy/docker-compose.yml
curl -O https://raw.githubusercontent.com/DAkmaev/stopportal/$branch/deploy/.env
curl -O https://raw.githubusercontent.com/DAkmaev/stopportal/$branch/deploy/.env.prod

# Copy environment variables if environment is "prod"
if [[ "$environment" == "prod" ]]; then
    cat .env.prod > .env
fi

# Load environment variables from .env file
set -a
source .env
set +a

sh ./backup_db.sh $environment

docker compose -f docker-compose.yml -p $environment pull
docker compose -f docker-compose.yml -p $environment down
docker compose -f docker-compose.yml -p $environment up -d
