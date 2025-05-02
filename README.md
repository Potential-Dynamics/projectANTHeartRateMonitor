This project contains a Python script designed to interface with an ANT+ heart rate monitor. It retrieves real-time heart rate data, making it suitable for fitness tracking or health monitoring applications.

### Acknowledgments

This project utilizes the [openant](https://github.com/Tigge/openant) library for ANT+ communication. Check the github page for setting up driver needed to connect to ANT+ devices.

### Environment 

python3 3.8.17
libusb1 3.3.1
openant 1.3.3
pyusb 1.2.1

### MQTT

This project uses Mosquitto for broadcasting heart rate data via MQTT. A `docker-compose.yml` file and a Mosquitto configuration file are provided under the `./docker` directory to simplify setup and deployment.

### How to use

To get started, you can either set up the environment manually by:

1. install the required libraries listed in the **Environment** section,

Note that the script is only tested with the specific versions of the libraries listed in the **Environment** section. (**only for single ANT+ device**)

2. use the pre-configured virtual environment provided by running ./run.bat.
