
import time
import json
import threading
import os

from collections import deque
from lib.mqtt_handler import MqttBaseCLass
from utils.utility_functions import read_ext_config
from utils.log import setup_logger, update_logger_verbose_level_from_config_file

from internal_broker_subscriber.internal_broker_subscriber import MosquittoMQTTSubscriber

logger = setup_logger()


def build_payload(logger, cloud_mqtt_broker_queue):
    if len(cloud_mqtt_broker_queue) != 0:
        payload = cloud_mqtt_broker_queue.popleft()
        payload = json.loads(payload)
        return json.dumps(payload)


def build_aggregatd_msg(logger, cloud_mqtt_broker_queue):
    payload = {}
    data = []
    while len(cloud_mqtt_broker_queue)>0:
        tag = cloud_mqtt_broker_queue.popleft()
        tag = json.loads(tag)
        if "data" in tag:
            tagList = tag["data"]
            for tag in tagList:
                # Insert your code for payload processing, enriching the data, normalization etc.
                data.append(tag)
    payload["data"] = data
    logger.debug("build_aggregatd_msg= {}".format(payload))
    return json.dumps(payload)


def publish_mqtt(ext_broker_publisher, logger, cloud_mqtt_broker_queue):
    """
    publish sample
    {"data": [{"modbusFC": "03-ReadHoldingRegisters",
                "deviceName": "pymodbus-win10-simulator",
                "tagName": "motorCurrent",
                "tagValue": 35911,
                "prvdName": "modbus_tcp_master",
                "ts": 1648650254710
                },

                {"modbusFC": "03-ReadHoldingRegisters",
                "deviceName": "pymodbus-win10-simulator",
                "tagName": "motorVoltage",
                "tagValue": 46509,
                "prvdName": "modbus_tcp_master",
                "ts": 1648650286283}]}

    """

    while True:
        payload = build_aggregatd_msg(logger, cloud_mqtt_broker_queue)
        #payload = build_payload(logger, cloud_mqtt_broker_queue)
        if payload is not None:
            mqtt_connection = ext_broker_publisher.is_open()
            if mqtt_connection is not False:
                logger.debug("Mqtt Connection OPEN! {}".format(mqtt_connection))
                ext_broker_publisher._client.publish(ext_broker_publisher._topic, (payload))
                logger.info("[Publish] = {} on topic {}".format(payload, ext_broker_publisher._topic))
            else:
                logger.error("Mqtt Connection CLOSED! {}".format(mqtt_connection))
        time.sleep(ext_broker_publisher._publish_interval)

def main():
    abs_path = os.path.dirname(os.path.realpath(__file__))
    #cloud_mqtt_broker_queue = Queue()
    cloud_mqtt_broker_queue = deque(maxlen=100)

    # Read configuretaion file into python object
    config_int_broker = read_ext_config(
        os.path.join(abs_path,'resources/config-internal-broker.json')
    )
    update_logger_verbose_level_from_config_file(logger, config_int_broker)

    int_broker_subscriber = MosquittoMQTTSubscriber(logger, cloud_mqtt_broker_queue, topic=config_int_broker["general"]["topic"])
    int_broker_subscriber.run()

    # Read configuretaion file into python object
    config_ext_broker = read_ext_config(
        os.path.join('resources/config-external-broker.json')
    )
    update_logger_verbose_level_from_config_file(logger, config_ext_broker)

    #Initialize MQTT
    ext_broker_publisher = MqttBaseCLass(conf = config_ext_broker)
    ext_broker_publisher.init_mqtt_client()
    ext_broker_publisher.connect_mqtt_broker()

    # Publish subscribe modbus messages to cloud mosquitto broker
    publish_mqtt(ext_broker_publisher, logger, cloud_mqtt_broker_queue)


if __name__ == '__main__':
    main()

