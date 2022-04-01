
import time 
import json 

from utils.utility_functions import read_ext_config

from utils.log import setup_logger, update_logger_verbose_level_from_config_file
from collections import deque

from internal_broker_subscriber.internal_broker_subscriber import MosquittoMQTTSubscriber

logger = setup_logger()

    
def start_mqtt_cloud_app(logger, topic, interval):
  
    cloud_mqtt_broker_queue = deque(maxlen=100)
    
    int_broker_subscriber = MosquittoMQTTSubscriber(logger, cloud_mqtt_broker_queue, topic)
    int_broker_subscriber.run()
 
    # Main loop start
    while True:
        time.sleep(interval)
        payload = process_payloads(logger, cloud_mqtt_broker_queue)
        if payload is not None:
            print("********  Process received payload for publishing into local HTTP Server for Data Visualization *****")
            print(payload)
    
    
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
        if len(cloud_mqtt_broker_queue) != 0:
            payload = cloud_mqtt_broker_queue.popleft()
            payload = json.loads(payload)
            # Insert your code for payload processing 
            return json.dumps(payload)
    except Exception as ex:
        logger.error("Caught an Exception when getting queue item. Exception {}:".format(ex))
        return

    
def main():
    
    # Read configuretaion file into python object 
    config_int_broker = read_ext_config('resources/config-internal-broker.json')
    update_logger_verbose_level_from_config_file(logger, config_int_broker)
    
    start_mqtt_cloud_app(logger, topic=config_int_broker["general"]["topic"], interval=config_int_broker["general"]["subscribe_interval"])
    
if __name__ == '__main__':
    main() 
    
