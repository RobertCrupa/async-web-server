# async-web-server
🚀 A simple ASGI webserver 

## Setting up Postgres docker database

1. Download the images `docker pull postgres`
2. Run with `docker run --name pg-container -p 8888:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=mydb -d postgres`