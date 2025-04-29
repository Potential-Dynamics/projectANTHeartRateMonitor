from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.heart_rate import HeartRateData, HeartRate
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "heart_rate/data"


def main(device_id_0=4755, device_id_1=19983):

    try:
        mqtt_client = mqtt.Client()
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:         
        print(f"Failed to connect to MQTT broker: {e}")
        print("Exiting...")
        return

    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    device0 = HeartRate(node, device_id=device_id_0)
    device1 = HeartRate(node, device_id=device_id_1)

    def create_callback(device_id):
        def on_device_data(page: int, page_name: str, data):
            if isinstance(data, HeartRateData):
                heart_rate = data.heart_rate
                print(f"Device ID {device_id}: Heart rate update {data.heart_rate}")
                payload = {
                        
                        "device_id": device_id,
                        "heart_rate": heart_rate,
                }
                mqtt_client.publish(MQTT_TOPIC, str(payload))
        return on_device_data

    # Bind the device_id to the callback
    device0.on_device_data = create_callback(device_id_0)
    device1.on_device_data = create_callback(device_id_1)

    try:
        node.start()
    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        # device.close_channel()
        node.stop()


if __name__ == "__main__":
    main()