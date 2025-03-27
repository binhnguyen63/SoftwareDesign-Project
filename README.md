Team Vernon

# COSC 4353 Project

HOW TO RUN THIS PROGRAM
You are able to run Dockerfile to start this program

step 1: create .env file with this format

CLIENT_ID=
CLIENT_SECRET=
PORT=5002
DB_HOST=host.docker.internal
DB_PORT=
DB_NAME=vernon
DB_USER=
DB_PASSWORD=

- Please dont change DB_HOST and PORT unless you are working with localhost (no dockerfile being used) and port 5002 does not work on your machine. If port number is changed, please adjust port number in docker run

step 2: build dockerfile

docker build -t vernon .

step 3: run dockerfile
docker run --env-file .env -p 5002:5002 vernon
