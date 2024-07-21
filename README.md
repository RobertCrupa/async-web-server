# async-web-server
🚀 A simple ASGI webserver

## Prerequisite

1. Python 3.10
2. poetry
3. docker

## Setting up Postgres docker database

1. Download the images `docker pull postgres`
2. Run with `docker run --name pg-container -p 8888:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mydb -d postgres`

## Running Web Server

1. Install requirements with poetry `poetry install`
2. Run server `poetry run uvicorn --workers 8 --log-level error main:app`
3. Open [homepage](http://127.0.0.1:8000/statics/index.html)