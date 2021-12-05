import asyncio
import os
from typing import List

from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from msrest.exceptions import HttpOperationError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.database import Base, SessionLocal, engine
from app import schemas, crud, auth

# Configuration
EVENT_CONNECTION_STR = os.getenv("EVENT_CONNECTION_STR")
REGISTRY_CONNECTION_STR = os.getenv("REGISTRY_CONNECTION_STR")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")

# App
app = FastAPI()


# Database
Base.metadata.create_all(bind=engine)
def get_db():
    """Return a database session and close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Websocket
websockets = {} # maps device IDs to websocket clients waiting for updates for that device

async def on_event(partition_context, event):
    event_body = event.body_as_json()
    if "device_id" in event_body:
        device_id = event_body["device_id"]
        if device_id in websockets:
            websocket = websockets[device_id]
            print("Forwarding event to client.")
            await websocket.send_text(event.body_as_str())
    await partition_context.update_checkpoint(event)

async def receive():
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_CONNECTION_STR,
        consumer_group=CONSUMER_GROUP,
        eventhub_name=EVENTHUB_NAME,
    )
    async with consumer_client:
        await consumer_client.receive(
            on_event=on_event,
            starting_position="@latest",  # "-1" is from the beginning of the partition.
        )

asyncio.create_task(receive())

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IoT Hub Registry Client
hub_registry_manager = IoTHubRegistryManager.from_connection_string(REGISTRY_CONNECTION_STR)

# Routes
@app.get("/devices/{device_id}/foodLevel", dependencies=[Depends(auth.validate_token)])
def getFoodLevel(device_id: str):
    try:
        twin = hub_registry_manager.get_twin(device_id)
        return {"foodLevel": twin.properties.reported["foodLevel"]}
    except HttpOperationError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.reason)


@app.get("/devices/{device_id}/unwelcomeVisitors", dependencies=[Depends(auth.validate_token)])
def read_device_unwelcome_visitors(device_id: str):
    try:
        twin = hub_registry_manager.get_twin(device_id)
        return {"unwelcomeVisitors": twin.properties.reported["unwelcomeVisitors"]}
    except HttpOperationError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.reason)


@app.post("/devices/{device_id}/unwelcomeVisitors", dependencies=[Depends(auth.validate_token)])
def update_device_unwelcome_visitors(device_id: str, unwelcome_visitors: schemas.UnwelcomeVisitorList):
    try:
        twin_patch = Twin()
        twin_patch.properties = TwinProperties(desired=unwelcome_visitors.dict())
        updated_twin = hub_registry_manager.update_twin(device_id, twin_patch)
        return updated_twin.properties.desired
    except HttpOperationError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.reason)


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    print(f"Accepted connection for {device_id}")
    websockets[device_id] = websocket
    try:
        while True:
            await websocket.receive_text() # detect when client disconnects
    except WebSocketDisconnect:
        del websockets[device_id]


@app.get("/visits/topSpecies", dependencies=[Depends(auth.validate_token)])
def get_top_species(limit: int = 10, db: Session = Depends(get_db)):
    top_species = crud.get_top_visiting_birds(db=db, limit=limit)
    return {"topSpecies": top_species}


@app.get("/users/{username}", response_model=schemas.User, dependencies=[Depends(auth.validate_token)])
def read_user_by_username(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}