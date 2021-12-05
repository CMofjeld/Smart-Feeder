# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import signal
import threading
import json
import datetime
from azure.iot.device.aio import IoTHubModuleClient
from object_tracker import ObjectTracker, TrackingInfo


# Event indicating client stop
stop_event = threading.Event()

# Tracker to help determine which objects have been previously seen
object_tracker = ObjectTracker()

# Minimum time that an object should be observed for before sending a visit message
tracking_duration_threshold = datetime.timedelta(seconds=1.0)


def construct_bird_visit_message(message_dict, timestamp):
    sensor = message_dict["sensor"]
    device_id = sensor["id"]
    latitude = sensor["location"]["lat"]
    longitude = sensor["location"]["lon"]
    species = message_dict["object"]["bird"]["species"]
    visit_message_dict = {
        "visiting_bird": species,
        "device_id": device_id,
        "visited_at": timestamp,
        "latitude": latitude,
        "longitude": longitude
    }
    return json.dumps(visit_message_dict)


def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()

    # Define function for handling received messages
    async def receive_message_handler(message):
        # NOTE: This function only handles messages sent to "input1".
        # Messages sent to other inputs, or to the default, will be discarded
        if message.input_name == "detection_messages":
            # Parse message as JSON
            message_dict = json.loads(message.data)

            # Get object detection data
            if not "object" in message_dict:
                print("Object detection data not found in message routed to detection_messages input")
                return
            object = message_dict["object"]

            # Get tracking ID
            if not "id" in object:
                print("Tracking ID not found in object detection data")
                return
            tracking_id = object["id"]

            # Print summary
            # Send message if the tracking duration exceeds the threshold
            global object_tracker
            global tracking_duration_threshold
            if object_tracker.contains(tracking_id):
                tracking_info = object_tracker.get_tracking_info(tracking_id)
                tracking_duration = datetime.datetime.now() - tracking_info.arrival_time
                if tracking_duration >= tracking_duration_threshold and not tracking_info.message_sent:
                    # Set message_sent to True to prevent duplicate messages
                    tracking_info.message_sent = True

                    if "bird" in object:
                        # Send message indicating a visit from a bird
                        output_message = construct_bird_visit_message(message_dict, tracking_info.arrival_time.isoformat())
                        await client.send_message_to_output(output_message, "bird_visits")
                    else:
                        # Non-bird visitor - alert the feeder in case they're unwelcome
                        device_id = message_dict["sensor"]["id"]
                        method_params = {
                            "methodName": "checkIfVisitorUnwelcome",
                            "responseTimeoutInSeconds": 30,
                            "connectTimeoutInSeconds": 20,
                            "payload": object
                        }
                        await client.invoke_method(method_params, device_id)
            else:
                object_tracker.start_tracking(tracking_id)

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise

    return client


async def busy_wait(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)


def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The module requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "Object Detection Analyzer" )

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()
    print("Finished creating client.")

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("Object Detection Analyzer module stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(busy_wait(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down Object Detection Analyzer...")
        loop.run_until_complete(client.shutdown())
        loop.close()


if __name__ == "__main__":
    main()
