# Smart-Feeder
IoT project to monitor and analyze visits to a bird feeder.

## Repository Structure
- [Feeder](https://github.com/CMofjeld/Smart-Feeder/tree/main/feeder) - Python module to control the Raspberry Pi attached to the bird feeder.
- [Backend API](https://github.com/CMofjeld/Smart-Feeder/tree/main/backend-api) - Backend API that the web/mobile app uses to interact with the system.
- [Bird classifier](https://github.com/CMofjeld/Smart-Feeder/tree/main/bird-classifier) - Code used to train and evaluate the secondary classifier that identifies bird species.
- [Deepstream](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream) - Modified code from the [Deepstream samples container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/deepstream-l4t) responsible for performing object detection, tracking, and classification. The modifications add the bird species in the detection messages sent to Azure IoT Hub.
- [Edge hub](https://github.com/CMofjeld/Smart-Feeder/tree/main/edge-hub) - Deployment configuration for the Azure IoT Edge modules running on the Jetson Nano.
  - [Object detection analyzer](https://github.com/CMofjeld/Smart-Feeder/tree/main/edge-hub/modules/ObjectDetectionAnalyzer) - Analyzes the stream of detection messages emitted by the [Deepstream](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream) module and translates them into discrete visit events.
- [Store bird visits in DB](https://github.com/CMofjeld/Smart-Feeder/tree/main/StoreBirdVisitsInDB) - Azure Stream Analytics job that parses visit messages emitted by the [Object detection analyzer](https://github.com/CMofjeld/Smart-Feeder/tree/main/edge-hub/modules/ObjectDetectionAnalyzer) and stores them in an Azure SQL Database.
- [Video player](https://github.com/CMofjeld/Smart-Feeder/tree/main/video-player) - Cross-platform application that lets the user view a live video stream of the feeder, monitor feeder food level, receive real-time notifications of bird visits, view past visit data, and configure the feeder.

## Acknowledgements
### General
During development for this project I benefitted greatly from the documentation and tutorials provided by Microsoft for [Azure IoT Hub](https://docs.microsoft.com/en-us/azure/iot-hub/), [Azure IoT Edge](https://docs.microsoft.com/en-us/azure/iot-edge/), [Azure Video Analyzer](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/), [Azure SQL](https://docs.microsoft.com/en-us/azure/azure-sql/), and [Azure Stream Analytics](https://docs.microsoft.com/en-us/azure/stream-analytics/).
### Code resources
If a software module used publicly available code resources, it is acknowledged in the documentation found in that subdirectory.