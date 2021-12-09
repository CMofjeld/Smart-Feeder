# Backend API
## Summary
This directory contains a FastAPI backend that the cross-platform app can use to interact with the IoT system.

## Configuration
The following environment variables need to be set for the backend to run properly.
```env
EVENT_CONNECTION_STR=<Event Hubs-compatible connection string to IoT Hub>
EVENTHUB_NAME=<Name of the IoT Hub>
CONSUMER_GROUP=<Consumer group the backend belongs to>
REGISTRY_CONNECTION_STR=<Azure IoT Hub connection string>
DB_SERVER=<Azure SQL Database URL>
DB_NAME=<Name of the database>
DB_USERNAME=<Database username>
DB_PASSWORD=<Database password>
DB_DRIVER=<Driver for accessing the database (needed by SQLAlchemy)>
DB_PORT=<Port to access database at>
SECRET_KEY=<Key for hashing passwords>
HASH_ALGORITHM=<Algorithm for hashing passwords>
```

## Testing the backend locally
To test the backend locally, create and activate a python environment with the listed requirements installed.
```bash
pip install -r requirements.txt
```
Start the server using uvicorn.
```bash
uvicorn app.main:app
```
Alternatively, you can build and run a Docker container using the provided Dockerfile. The container's default command will start the backend on startup.

## Deploying
1. Build a custom container using the provided Dockerfile.
2. Push the image to a container registry.
3. Create an [Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/quickstart-custom-container?tabs=dotnet&pivots=container-linux), using a custom container as the source.

## Acknowledgments
Code provided in the FastAPI tutorials on [security](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) and [interacting with a SQL database](https://fastapi.tiangolo.com/tutorial/sql-databases/) was used as a starting point for this backend.