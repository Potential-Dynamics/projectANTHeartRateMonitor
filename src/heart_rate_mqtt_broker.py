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
import argparse
import sys

# Uncomment the following lines to enable debug logging for openant

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

sys.stdout.reconfigure(line_buffering=True) 

# MQTT Configuration, CHANGE if needed
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "heart_rate/data"

def run_node(node, node_name):
    try:
        print(f"Start {node_name}...")
        node.start()
    except Exception as e:
        print(f"Error in {node_name}: {e}")


def main(device_ids): 
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

        node2 = Node()
        node2.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

        node3 = Node()
        node3.set_network_key(0x00, ANTPLUS_NETWORK_KEY)
    except Exception as e:
        # traceback.print_exc()
        print(f"Failed to initialize ANT+ node: {e}")
        print("Check your ANT+ dongle again.")
        print("Exiting...")
        time.sleep(5)
        return

    devices = []
    nodes = [node0, node1, node2, node3]
    for i, node in enumerate(nodes):
        for j in range(8):  # Each node handles 8 devices
            device_index = i * 8 + j
            devices.append(HeartRate(node, device_id=device_ids[device_index]))

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

    for i, device in enumerate(devices):
        node_serial_number = nodes[i // 8].serial  # Determine the node based on the device index
        device.on_device_data = create_callback(device_ids[i], node_serial_number)


    node0_thread = threading.Thread(target=run_node, args=(node0, "node0"))
    node1_thread = threading.Thread(target=run_node, args=(node1, "node1"))
    node2_thread = threading.Thread(target=run_node, args=(node2, "node2"))
    node3_thread = threading.Thread(target=run_node, args=(node3, "node3"))


    try:
        node0_thread.start()
        node1_thread.start()
        node2_thread.start()
        node3_thread.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        # device.close_channel()
        node0.stop()
        node1.stop()
        node2.stop()
        node3.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start ANT+ Heart Rate Monitor with MQTT.")
    parser.add_argument("device_ids", metavar="ID", type=int, nargs=32,
                        help="Nine device IDs in order (device_id_0 to device_id_31)")
    args = parser.parse_args()
    main(args.device_ids)