# Edge hub
## Summary
This directory contains deployment configuration for the Azure IoT Edge modules running on the Jetson Nano and code for the Object Detection Analyzer module.

## Structure
- Root directory - Azure IoT Edge deployment templates.
- [modules/ObjectDetectionAnalyzer](https://github.com/CMofjeld/Smart-Feeder/tree/main/edge-hub/modules/ObjectDetectionAnalyzer) - Analyzes the stream of detection messages emitted by the [Deepstream](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream) module and translates them into discrete visit events.

## Configuration
In the root directory, create a .env file containing definitions for the following environment variables:
```env
SUBSCRIPTION_ID=<Azure subscription ID>
RESOURCE_GROUP=<Azure resource group>
AVA_PROVISIONING_TOKEN=<Provisioning token for Azure Video Analyzer edge module>
VIDEO_INPUT_FOLDER_ON_DEVICE=<Path to sample video input directory for AVA module on edge device>
VIDEO_OUTPUT_FOLDER_ON_DEVICE=<Path to video output directory for AVA module on edge device>
APPDATA_FOLDER_ON_DEVICE=<Path to app data directory for AVA module on edge device>
CONTAINER_REGISTRY_USERNAME_myacr=<Username for Azure Container Registry>
CONTAINER_REGISTRY_PASSWORD_myacr=<Password for Azure Container Registry>
```