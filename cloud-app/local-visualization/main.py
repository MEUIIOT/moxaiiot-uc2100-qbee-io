import requests
import time
import json
import os
import copy

from utils.utility_functions import read_ext_config

from utils.log import setup_logger, update_logger_verbose_level_from_config_file,update_logger_verbose_level
from collections import deque

from internal_broker_subscriber.internal_broker_subscriber import MosquittoMQTTSubscriber
from logging.handlers import RotatingFileHandler

logger = setup_logger()
#handler = RotatingFileHandler('/home/moxa/application/logs/vis.log', maxBytes=2000000,
#                              backupCount=0)
#logger.addHandler(handler)

def start_mqtt_cloud_app(logger, topic, interval, transformation_config, plot_server_config):

    cloud_mqtt_broker_queue = deque(maxlen=100)

    int_broker_subscriber = MosquittoMQTTSubscriber(logger, cloud_mqtt_broker_queue, topic)
    int_broker_subscriber.run()

    plot_server_url = "http://%s:%d"%(plot_server_config["host"] , plot_server_config["port"])

    # Main loop start
    while True:
        process_payloads(logger, cloud_mqtt_broker_queue, transformation_config, plot_server_url)
        time.sleep(interval)
        #if payload is not None:
        #    print("\n")
        #    print("********  Process received payload for publishing into local HTTP Server for Data Visualization *****")
        #    #print(payload)
        #    send_to_server(payload)
        #    print("sleep interval is: ", interval)
        #    print("\n")


def process_payloads(logger, cloud_mqtt_broker_queue, transformation_config,plot_server_url):
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
            payload = apply_unit_transformation(payload,transformation_config)
            send_to_server(payload,plot_server_url)
    except Exception as ex:
        logger.error("Caught an Exception when getting queue item. Exception {}:".format(ex))
        return

def apply_unit_transformation(payload,transformation_config):
    data_arr = payload["data"]
    for item in data_arr:
        tagName = item["tagName"]
        if( tagName in transformation_config ):
            ## get params
            enabled = transformation_config[tagName]["enabled"]
            # skip if not enabled
            if(not enabled):
                continue
            tRange = transformation_config[tagName]["range"]
            length = transformation_config[tagName]["length"]
            unit = transformation_config[tagName]["unit"]
            suffix = transformation_config[tagName]["suffix"]
            ## apply trafo
            old_val = item["tagValue"]
            new_val = old_val / length * (tRange[1] - tRange[0]) + tRange[0]
            ## title
            newTagName = tagName + suffix
            # overwrite or copy

            item["tagName"] = newTagName
            item["tagValue"] = new_val
            item["unit"] = unit

    payload["data"] = data_arr
    return payload

def send_to_server(payload,url):

    data_arr = payload["data"]
    for item in data_arr:
        data = {'tag': item["tagName"],'value': item["tagValue"], 'ts': item["ts"], 'unit': item.get('unit')}
        print(data)
        requests.post(url,json=data)


def main():
    abs_path = os.path.dirname(os.path.realpath(__file__))
    # Read configuretaion file into python object
    config_int_broker = read_ext_config(
        os.path.join(abs_path,'resources/config-internal-broker.json')
    )

    config_transformation = read_ext_config(
        os.path.join(abs_path, 'resources/transformation_config.json')
    )

    config_plot_server = read_ext_config(
        os.path.join(abs_path, 'resources/plot_server.json')
    )

    update_logger_verbose_level_from_config_file(logger, config_int_broker)

    start_mqtt_cloud_app(logger, topic=config_int_broker["general"]["topic"],
                            interval=config_int_broker["general"]["subscribe_interval"],
                            transformation_config=config_transformation,
                            plot_server_config=config_plot_server
    )

if __name__ == '__main__':
    main()

