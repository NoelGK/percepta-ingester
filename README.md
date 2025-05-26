# PERCEPTA

## Deploy service
In order to run the service, you must have access to a running Redis instance.

Copy the file `.env-local` to a file called `.env`, and then fill in your corresponding credentials.

Then, run in your terminal:
```
docker network create percepta
docker build -t percepta-ingester:latest .
docker compose up
```

## Manager API
The streams ingested by the service are handeled by an API whose documentation can be consulted at http://localhost:8000/docs. The supported actions are:

- Add a new stream
- Remove an existing stream
- Consult existing streams
