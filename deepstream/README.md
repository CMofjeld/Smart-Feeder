# Deepstream
## Summary
Code, configuration, and resources for the Deepstream module that performs object detection, tracking, and classification on a Jetson Nano.

## Structure
- [Deepstream Test 5](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream/deepstream-test5) - Code for the Deepstream application. It has been modified from the original to also include bird species in its cloud messages. Also contains a binary compiled on the Jetson Nano platform (deepstream-test5-app).
- [Nvmsgconv](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream/nvmsgconv) - Updated library for generating and sending the modified messages described above. Also contains the library shared object compiled on the Jetson Nano platform (libnvds_msgconv.so).
- [Bird detection](https://github.com/CMofjeld/Smart-Feeder/tree/main/deepstream/bird-detection) - Configuration and model files necessary to run the intended workload with the modified Deepstream app.

## Running the module
Build a container image using the provided Dockerfile and push it to a remote repository. Specify the module in an Azure IoT Edge deployment configuration. Copy the bird-detection subdirectory to the machine that will run the module. In the Edge deployment, mount the copied subdirectory as a volume of the container and specify the run command "-c [path to mounted directory in container]/bird-detector-config.txt -t".

To run the module as a standalone container outside of the IoT Edge ecosystem, the sink that sends messages to Azure IoT must be disabled. To do so, open bird-detector-config.txt, find the section for [Sink 3], and set enable equal to 0.

## Acknowledgements
The original code for the Deepstream app, Nvmsgconv library, and Deepstream configuration file examples were taken from the [Deepstream-l4t:5.1-21.02-samples](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/deepstream-l4t) container image provided by Nvidia.