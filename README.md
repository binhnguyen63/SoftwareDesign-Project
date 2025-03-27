# Team Vernon

## COSC 4353 Project

### How to Run the Program

You can run this program using the **Dockerfile**. Follow the steps below to get started.

---

### Step 1: Create the `.env` File

Create a `.env` file in your project directory with the following format:

```env
CLIENT_ID=
CLIENT_SECRET=
PORT=5002
DB_HOST=host.docker.internal
DB_PORT=
DB_NAME=vernon
DB_USER=
DB_PASSWORD=
```

- Important:

* Do not change DB_HOST and PORT unless you're working locally (without Docker).

* If port 5002 does not work on your machine, feel free to change the port number, but ensure to update the port number in the docker run command accordingly.

### Step 2: Build the Docker image

run the following command:

```
docker build -t vernon .
```

- This command will create a Docker image named vernon.

### Step 3: Run THe Docker Container

docker run --env-file .env -p 5002:5002 vernon

- Please match the port to the port number specified in env file
