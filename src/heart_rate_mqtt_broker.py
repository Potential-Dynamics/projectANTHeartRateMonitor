from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.heart_rate import HeartRateData, HeartRate
import time
import os
import traceback
import paho.mqtt.client as mqtt
import logging
import importlib
import threading

# logging.basicConfig(
#     level=logging.INFO,  # Set to DEBUG to see all logs
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),  # Output to console
#         logging.FileHandler('openant_debug.log')  # Also save to a file
#     ]
# )
# # Get the logger specifically for openant
# openant_logger = logging.getLogger('openant')
# openant_logger.setLevel(logging.INFO)  # Set to DEBUG, INFO, WARNING, ERROR as needed


# MQTT Configuration, CHANGE if needed
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "heart_rate/data"

def run_node(node, node_name):
    try:
        print(f"Starting {node_name}...")
        node.start()
        print(f"{node_name} started successfully")
    except Exception as e:
        print(f"Error in {node_name}: {e}")


def main(device_id_0=4755, device_id_1=19983, device_id_2=62618, device_id_3=26270, device_id_4= 33630, device_id_5=40571, device_id_6=16245):

    try:
        mqtt_client = mqtt.Client()
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:         
        print(f"Failed to connect to MQTT broker: {e}")
        print("Exiting...")
        time.sleep(5)
        return

    try :
        node0 = Node()
        node0.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        node1 = Node()
        node1.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    except Exception as e:
        # traceback.print_exc()
        print(f"Failed to initialize ANT+ node: {e}")
        print("Check your ANT+ dongle again.")
        print("Exiting...")
        time.sleep(5)
        return

    device0 = HeartRate(node1, device_id=device_id_0)
    device1 = HeartRate(node0, device_id=device_id_1)
    device2 = HeartRate(node0, device_id=device_id_2)
    device3 = HeartRate(node0, device_id=device_id_3)
    device4 = HeartRate(node0, device_id=device_id_4)
    device5 = HeartRate(node0, device_id=device_id_5)
    device6 = HeartRate(node0, device_id=device_id_6)

    def create_callback(device_id, node_serial_number):
        def on_device_data(page: int, page_name: str, data):
            if isinstance(data, HeartRateData):
                heart_rate = data.heart_rate
                if heart_rate >= 50:
                    log_dir = "./log"
                    os.makedirs(log_dir, exist_ok=True)
                    with open(os.path.join(log_dir, "node_channels.log"), "a") as log_file:
                        log_file.write(f"{node_serial_number}\n")
                    print(f"Device ID {device_id}: Heart rate update {data.heart_rate}")
                    payload = {
                            
                            "device_id": device_id,
                            "heart_rate": heart_rate,
                    }
                    mqtt_client.publish(MQTT_TOPIC, str(payload))
        return on_device_data

    # Bind the device_id to the callback
    device0.on_device_data = create_callback(device_id_0, node1.serial)
    device1.on_device_data = create_callback(device_id_1, node0.serial)
    device2.on_device_data = create_callback(device_id_2, node0.serial)
    device3.on_device_data = create_callback(device_id_3, node0.serial)
    device4.on_device_data = create_callback(device_id_4, node0.serial)
    device5.on_device_data = create_callback(device_id_5, node0.serial)
    device6.on_device_data = create_callback(device_id_6, node0.serial)

    node0_thread = threading.Thread(target=run_node, args=(node0, "node0"))
    node1_thread = threading.Thread(target=run_node, args=(node1, "node1"))


    try:
        node0_thread.start()
        node1_thread.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        # device.close_channel()
        node0.stop()
        node1.stop()


if __name__ == "__main__":
    main()