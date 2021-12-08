"""Controls the distance sensor and buzzer attached to the bird feeder and communicates with the IoT Hub.

This code used the Azure IoT Hub sample code found at this URL as a starting point:
https://github.com/Azure/azure-iot-sdk-python/blob/main/azure-iot-device/samples/async-hub-scenarios/receive_twin_desired_properties_patch.py
The original copyright notice is preserved below.
"""
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from six.moves import input
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import MethodResponse
import board
import busio
import adafruit_vl53l0x
import RPi.GPIO as GPIO
import datetime

# Default config values for feeder
MAX_DIST = 135
MIN_DIST = 110
FOOD_POLL = 5

# Default config values for alarm
BUZZER_PIN = 26
ALARM_INTERVAL = 0.5
ALARM_REPS = 5 
UNWELCOME_VISITORS = ["bear", "cat", "dog"]

class DistanceSensor:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl53l0x.VL53L0X(i2c)
        self.sensor.measurement_timing_budget = 800000
    
    def range(self):
        return self.sensor.range


class Alarm:
    def __init__(self, buzzer_pin=BUZZER_PIN) -> None:
        self.buzzer_pin = buzzer_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(buzzer_pin, GPIO.OUT, initial=GPIO.LOW)
        self.sounding_alarm = False

    async def sound_alarm(self, interval=ALARM_INTERVAL, repetitions=ALARM_REPS):
        if not self.sounding_alarm:
            self.sounding_alarm = True
            for _ in range(repetitions):
                GPIO.output(self.buzzer_pin, GPIO.HIGH)
                await asyncio.sleep(interval)
                GPIO.output(self.buzzer_pin, GPIO.LOW)
                await asyncio.sleep(interval)
            self.sounding_alarm = False


class Feeder:
    def __init__(self, max_food_distance, min_food_distance, food_poll_interval, buzzer_pin=BUZZER_PIN, unwelcome_visitors=[]) -> None:
        self.distance_sensor = DistanceSensor()
        self.max_food_distance = max_food_distance
        self.min_food_distance = min_food_distance
        self.max_food_height = max_food_distance - min_food_distance
        self.food_poll_interval = food_poll_interval
        self.update_food_level()
        self.alarm = Alarm(buzzer_pin)
        self.set_unwelcome_visitors(unwelcome_visitors)

    def update_food_level(self):
        cur_distance = self.distance_sensor.range()
        cur_height = self.max_food_distance - cur_distance
        calculated_food_level = cur_height / self.max_food_height
        self.food_level = max(min(calculated_food_level, 1.0), 0.0)

    def get_food_level(self):
        return self.food_level

    def set_food_pool_interval(self, new_interval):
        self.food_poll_interval = new_interval

    def set_unwelcome_visitors(self, new_unwelcome_visitors):
        self.unwelcome_visitors = set(new_unwelcome_visitors)

    async def send_periodic_food_level_updates(self, client):
        while True:
            self.update_food_level()
            reported_level = {"foodLevel": self.food_level}
            await client.patch_twin_reported_properties(reported_level)
            await asyncio.sleep(self.food_poll_interval)

    async def sound_alarm(self):
        await self.alarm.sound_alarm()


def get_desired_prop(desired_prop_dict, prop_dict_key, prop_env_key, prop_default):
    if prop_dict_key in desired_prop_dict:
        return desired_prop_dict[prop_dict_key]
    else:
        return os.getenv(prop_env_key, prop_default)


async def report_feeder_properties(feeder, client):
    report = {
        "distanceConfig": {
            "maxFoodDistance": feeder.max_food_distance,
            "minFoodDistance": feeder.min_food_distance,
            "foodPollInterval": feeder.food_poll_interval,
        },
        "foodLevel": feeder.food_level,
        "unwelcomeVisitors": list(feeder.unwelcome_visitors)
    }
    await client.patch_twin_reported_properties(report)

async def main():
    # connect the client.
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
    ca_path = os.getenv("IOTEDGE_ROOT_CA_CERT_PATH")
    with open(ca_path, "r") as ca_file:
        root_ca_cert = ca_file.read()
    device_client = IoTHubDeviceClient.create_from_connection_string(
        connection_string=conn_str,
        server_verification_cert=root_ca_cert)
    await device_client.connect()

    # get desired properties from device twin or environment
    twin = await device_client.get_twin()
    if "distanceConfig" in twin["desired"]:
        distance_config = twin["desired"]["distanceConfig"]
    else:
        distance_config = {}
    max_food_distance = get_desired_prop(distance_config, "maxFoodDistance", "MAX_FOOD_DIST", MAX_DIST)
    min_food_distance = get_desired_prop(distance_config, "minFoodDistance", "MIN_FOOD_DIST", MIN_DIST)
    food_poll_interval = get_desired_prop(distance_config, "foodPollInterval", "FOOD_POLL_INT", FOOD_POLL)
    unwelcome_visitors = get_desired_prop(twin["desired"], "unwelcomeVisitors", "UNWELCOME_VISITORS", UNWELCOME_VISITORS)
    if type(unwelcome_visitors) == str:
        # Got list of unwelcome visitors from environment variable - need to parse into a list
        unwelcome_visitors = unwelcome_visitors.split(",")

    # create the feeder object
    feeder = Feeder(max_food_distance, min_food_distance, food_poll_interval, unwelcome_visitors=unwelcome_visitors)

    # define behavior for receiving a twin patch
    # NOTE: this could be a function or a coroutine
    async def twin_patch_handler(patch):
        if "distanceConfig" in patch:
            distance_config = patch["distanceConfig"]
            if "foodPollInterval" in distance_config:
                new_interval = distance_config["foodPollInterval"]
                print(f"Updating food poll interval to {new_interval}")
                feeder.set_food_pool_interval(new_interval)
        if "unwelcomeVisitors" in patch:
            unwelcome_visitors = patch["unwelcomeVisitors"]
            print(f"Updating unwelcome visitors to {unwelcome_visitors}")
            feeder.set_unwelcome_visitors(unwelcome_visitors)
        else:
            print("Updating unknown desired property.")
        await report_feeder_properties(feeder, device_client)

    # set the twin patch handler on the client
    device_client.on_twin_desired_properties_patch_received = twin_patch_handler

    # Define behavior for handling methods
    async def method_request_handler(method_request):
        # Determine how to respond to the method request based on the method name
        if method_request.name == "checkIfVisitorUnwelcome":
            object = method_request.payload
            if not set(object).isdisjoint(feeder.unwelcome_visitors):
                # Unwelcome visitor - sound the alarm
                data = "Visitor unwelcome - sounding alarm"
                print(f"Sounding alarm at {datetime.datetime.today()}")
                #asyncio.create_task(feeder.sound_alarm())
            else:
                # Visitor not unwelcome - do nothing
                data = "Visitor not unwelcome - not sounding alarm"
                print(f"Visitor not unwelcome - not sounding alarm at {datetime.datetime.today()}")
            payload = {"result": True, "data": data}
            status = 200  # set return status code
        else:
            payload = {"result": False, "data": "unknown method"}  # set response payload
            status = 400  # set return status code
            print("Received request for unknown method: " + method_request.name)
        # Send the response
        method_response = MethodResponse.create_from_method_request(method_request, status, payload)
        await device_client.send_method_response(method_response)

    # Set the method request handler on the client
    device_client.on_method_request_received = method_request_handler

    # report current properties
    await report_feeder_properties(feeder, device_client)

    # start periodic updates
    periodic_updates = asyncio.create_task(feeder.send_periodic_food_level_updates(device_client))

    # define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for messages
    await user_finished

    # Stop the periodic updates
    periodic_updates.cancel()

    # Finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())