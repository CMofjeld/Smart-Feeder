import asyncio
import json
import os

from azure.eventhub.aio import EventHubConsumerClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from msrest.exceptions import HttpOperationError

app = FastAPI()

# Configuration
EVENT_CONNECTION_STR = os.getenv("EVENT_CONNECTION_STR")
REGISTRY_CONNECTION_STR = os.getenv("REGISTRY_CONNECTION_STR")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")

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
@app.get("/devices/{device_id}/foodLevel")
def getFoodLevel(device_id: str):
    try:
        twin = hub_registry_manager.get_twin(device_id)
        return {"foodLevel": twin.properties.reported["foodLevel"]}
    except HttpOperationError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.reason)


@app.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    print(f"Accepted connection for {device_id}")
    await websocket.send_text(f"Listening for notifications for: {device_id}")
    websockets[device_id] = websocket
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)
