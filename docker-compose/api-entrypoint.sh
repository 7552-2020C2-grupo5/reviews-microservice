#!/bin/bash
docker-compose/wait-for-postgres.sh

echo 'creating db'
poetry run python reviews_microservice/manage.py db_create
echo 'upgrading db'
poetry run python reviews_microservice/manage.py db upgrade
echo 'starting server'
poetry run gunicorn -w 2 --bind 0.0.0.0:5000 "reviews_microservice.app:create_app()"
