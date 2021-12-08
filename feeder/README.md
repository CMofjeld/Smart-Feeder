# Feeder
## Summary
This software module controls the distance sensor and buzzer attached to the bird feeder and communicates with the IoT Hub. To connect to the Hub, a device connection string must be provided as the value for the environment variable IOTHUB_DEVICE_CONNECTION_STRING. The module is written under the assumption that it will be run on a Raspberry Pi. A Dockerfile is included for building and running the module as a container.

To function properly, the system assumes that the feeder will also be streaming video from its camera over RTSP. One option for doing so is the open-source [v4l2rtspserver](https://github.com/mpromonet/v4l2rtspserver).

## Code resources
main.py used the code for [this Azure IoT Hub sample](https://github.com/Azure/azure-iot-sdk-python/blob/main/azure-iot-device/samples/async-hub-scenarios/receive_twin_desired_properties_patch.py) as a starting point.