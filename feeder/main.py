# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubDeviceClient
import board
import busio
import adafruit_vl53l0x

# Default config values for feeder
DEFAULT_MAX_DIST = 120
DEFAULT_MIN_DIST = 90
DEFAULT_FOOD_POLL = 5

class DistanceSensor:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl53l0x.VL53L0X(i2c)
    
    def range(self):
        return self.sensor.range


class Feeder:
    def __init__(self, max_food_distance, min_food_distance, food_poll_interval) -> None:
        self.distance_sensor = DistanceSensor()
        self.max_food_distance = max_food_distance
        self.min_food_distance = min_food_distance
        self.max_food_height = max_food_distance - min_food_distance
        self.food_poll_interval = food_poll_interval
        self.update_food_level()

    def update_food_level(self):
        cur_distance = self.distance_sensor.range()
        cur_height = self.max_food_distance - cur_distance
        calculated_food_level = cur_height / self.max_food_height
        self.food_level = min(calculated_food_level, 1.0)

    def get_food_level(self):
        return self.food_level

    def set_food_pool_interval(self, new_interval):
        self.food_poll_interval = new_interval

    async def send_periodic_food_level_updates(self, client):
        while True:
            self.update_food_level()
            reported_level = {"foodLevel": self.food_level}
            await client.patch_twin_reported_properties(reported_level)
            await asyncio.sleep(self.food_poll_interval)


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
        "foodLevel": feeder.food_level
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
    max_food_distance = get_desired_prop(distance_config, "maxFoodDistance", "MAX_FOOD_DIST", DEFAULT_MAX_DIST)
    min_food_distance = get_desired_prop(distance_config, "minFoodDistance", "MIN_FOOD_DIST", DEFAULT_MIN_DIST)
    food_poll_interval = get_desired_prop(distance_config, "foodPollInterval", "FOOD_POLL_INT", DEFAULT_FOOD_POLL)

    # create the feeder object
    feeder = Feeder(max_food_distance, min_food_distance, food_poll_interval)

    # define behavior for receiving a twin patch
    # NOTE: this could be a function or a coroutine
    def twin_patch_handler(patch):
        print("the data in the desired properties patch was: {}".format(patch))

    # set the twin patch handler on the client
    device_client.on_twin_desired_properties_patch_received = twin_patch_handler

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