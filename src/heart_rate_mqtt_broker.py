from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.heart_rate import HeartRateData, HeartRate

def main(device_id_0=4755, device_id_1=19983):
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    device0 = HeartRate(node, device_id=device_id_0)
    device1 = HeartRate(node, device_id=device_id_1)

    def create_callback(device_id):
        def on_device_data(page: int, page_name: str, data):
            if isinstance(data, HeartRateData):
                print(f"Device ID {device_id}: Heart rate update {data.heart_rate}")
        return on_device_data

    # Bind the device_id to the callback
    device0.on_device_data = create_callback(4755)
    device1.on_device_data = create_callback(19983)

    try:
        node.start()
    except KeyboardInterrupt:
        print("Closing ANT+ device...")
    finally:
        # device.close_channel()
        node.stop()


if __name__ == "__main__":
    main()