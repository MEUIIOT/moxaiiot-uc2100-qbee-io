import requests
import time
import json
import os

from utils.utility_functions import read_ext_config

from utils.log import setup_logger, update_logger_verbose_level_from_config_file,update_logger_verbose_level
from collections import deque

from internal_broker_subscriber.internal_broker_subscriber import MosquittoMQTTSubscriber

logger = setup_logger()


def start_mqtt_cloud_app(logger, topic, interval):

    cloud_mqtt_broker_queue = deque(maxlen=100)

    int_broker_subscriber = MosquittoMQTTSubscriber(logger, cloud_mqtt_broker_queue, topic)
    int_broker_subscriber.run()

    # Main loop start
    while True:
        process_payloads(logger, cloud_mqtt_broker_queue)
        time.sleep(interval)
        #if payload is not None:
        #    print("\n")
        #    print("********  Process received payload for publishing into local HTTP Server for Data Visualization *****")
        #    #print(payload)
        #    send_to_server(payload)
        #    print("sleep interval is: ", interval)
        #    print("\n")


def process_payloads(logger, cloud_mqtt_broker_queue):
    """
    Received payload sample
    {
	"data": [{
		"modbusFC": "03-ReadHoldingRegisters",
		"tagName": "motorCurrent",
		"tagValue": 5090,
		"deviceName": "pymodbus-win10-simulator",
		"prvdName": "modbus_tcp_master",
		"ts": 1648768182768
	}, {
		"modbusFC": "03-ReadHoldingRegisters",
		"tagName": "motorVoltage",
		"tagValue": 18613,
		"deviceName": "pymodbus-win10-simulator",
		"prvdName": "modbus_tcp_master",
		"ts": 1648768182788
	}, {
		"modbusFC": "03-ReadHoldingRegisters",
		"tagName": "motorPower",
		"tagValue": 47631,
		"deviceName": "pymodbus-win10-simulator",
		"prvdName": "modbus_tcp_master",
		"ts": 1648768182808
	}]
    }
    """
    try:
        while len(cloud_mqtt_broker_queue) != 0:
            payload = cloud_mqtt_broker_queue.popleft()
            payload = json.loads(payload)
            # Insert your code for payload processing
            #return payload #json.dumps(payload)
            send_to_server(payload)
    except Exception as ex:
        logger.error("Caught an Exception when getting queue item. Exception {}:".format(ex))
        return

def send_to_server(payload):

    host = 'localhost'
    port = 8080
    url = "http://" + host + ":" + str(port)

    data_arr = payload["data"]
    for item in data_arr:
        data = {'tag': item["tagName"],'value': item["tagValue"], 'ts': item["ts"]}
        print(data)
        requests.post(url,json=data)


def main():
    abs_path = os.path.dirname(os.path.realpath(__file__))
    # Read configuretaion file into python object
    config_int_broker = read_ext_config(
        os.path.join(abs_path,'resources/config-internal-broker.json')
    )
    update_logger_verbose_level_from_config_file(logger, config_int_broker)
    update_logger_verbose_level(logger,1)

    start_mqtt_cloud_app(logger, topic=config_int_broker["general"]["topic"], interval=config_int_broker["general"]["subscribe_interval"])

if __name__ == '__main__':
    main()

