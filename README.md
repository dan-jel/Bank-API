# Bank-API

Eine restful API die die Funktionalität einer Bank imitiert.

<br>

## API-Routes:

- `/register` | to register a new user

```json
{
  "username": "***",
  "password": "***"
}
```

- `/add` | to add money to your account

```json
{
  "username": "***",
  "password": "***",
  "amount": 999
}
```

- `/transfer` | to send money to another user

```json
{
  "username": "***",
  "password": "***",
  "to": "***",
  "amount": 999
}
```

- `/balance` | to check your accounts balance

```json
{
  "username": "***",
  "password": "***"
}
```

- `/takeloan` | to receive a credit from the bank

```json
{
  "username": "***",
  "password": "***",
  "amount": 999
}
```

- `/payloan` | to pay back your credit from the bank

```json
{
  "username": "***",
  "password": "***",
  "amount": 999
}
```

<br>

## Set up the Docker Container

1. to build the image from the Dockerfile

```bash
sudo docker-compose build
```

2. to run the docker containers build by the `.yml`

```bash
sudo docker-compose up
```

## Check the DB

in the `docker-compose.yml` you can see, that I map the default MongoDB Port to the hostmachine, which is not neccesary for the API to work.

```yml
version: "3"

services:
  web:
    build: ./web
    ports:
      - "5000:5000"
    links:
      - db

  db:
    build: ./db
    ports:
      - "27017:27017"
```

So you can access the Database easily via MongoDB Compass under `mongodb://localhost:27017`.
