import sys
import time
import json
import logging
import threading
import os

from collections import deque

#from pymodbus.payload import BinaryPayloadDecoder

from lib.mqtt_handler import MqttBaseCLass
from lib.tcp_handler import TCPConnectionHandler
from lib.serial_handler import SerialConnectionHandler
from lib.modbus_tcp_master import read_modbus_tcp_loop
from lib.modbus_rtu_master import read_modbus_rtu_loop

from utils.utility_functions import read_ext_config, parse_modbus_template, read_modbus_master_config

from utils.log import setup_logger, update_logger_verbose_level_from_config_file


logger = setup_logger()


def modbus_to_mqtt(mqtt, payload):
    if payload is not None:
        # Publish to internal MQTT broker
        mqtt_connection = mqtt.is_open()
        if mqtt_connection is not False:
            logger.debug("Mqtt Connection OPEN! {}".format(mqtt_connection))
            #payload = json.dumps(payload)
            mqtt._client.publish(mqtt._topic, (payload))
            logger.info("[Publish] = {}".format(payload))
        else:
            logger.error("Mqtt Connection CLOSED! {}".format(mqtt_connection))


def build_aggregatd_msg(device_name, modbus_response_deque, modbus_tcp_master, modbus_rtu_master):
    payload = {}
    data = []
    while len(modbus_response_deque)>0:
        tag = modbus_response_deque.popleft()
        # Add additional info modbus deviceName and prvdName in the payload received via queue
        if modbus_rtu_master["enable"]:
            tag["prvdName"] = "modbus_rtu_master" 
        if modbus_tcp_master["enable"]:
            tag["prvdName"] = "modbus_tcp_master"
        tag["deviceName"] = device_name
        data.append(tag)
    payload["data"] = data
    logger.debug("build_aggregatd_msg= {}".format(payload))
    return json.dumps(payload)


def build_payload(device_name, modbus_response_deque):
    if len(modbus_response_deque) != 0:
        # add provider name tcp or rtu
        payload = modbus_response_deque.popleft()
        # Add additional info modbus deviceName and prvdName in the payload received via queue
        payload["prvdName"] = "modbus_tcp_master" # static needs to be added dynamically in case modbus rtu device is also enable
        payload["deviceName"] = device_name
        return json.dumps(payload)


def publish_mqtt(mqtt, device_name, modbus_response_deque, modbus_tcp_master, modbus_rtu_master):
    while True:
        # Publish to MQTT broker
        payload = build_aggregatd_msg(device_name, modbus_response_deque, modbus_tcp_master, modbus_rtu_master)
        #payload = build_payload(device_name, modbus_response_deque)
        modbus_to_mqtt(mqtt, payload)
        time.sleep(mqtt._publish_interval)

def main():
    abs_path = os.path.dirname(os.path.realpath(__file__))
    print("ABSOLUTE PATH:", abs_path)
    """
    # Read configuretaion file into python object
    config_mqtt_broker = read_ext_config('resources/config-internal-broker.json')
    """
    config_mqtt_broker = read_ext_config(
        os.path.join(abs_path, 'resources/config-internal-broker.json'))
    
    ## Initialize MQTT
    mqtt = MqttBaseCLass(conf = config_mqtt_broker)
    mqtt.init_mqtt_client()
    mqtt.connect_mqtt_broker()
    """
    # Config logging for console output
    filename = 'resources/config-modbus-master.json'
    json_file = read_ext_config(filename)
    update_logger_verbose_level_from_config_file(logger, config_file_obj=json_file)
    """
    # Config logging for console output
    filename = 'resources/config-modbus-master.json'
    json_file = read_ext_config( os.path.join(abs_path, filename) )
    update_logger_verbose_level_from_config_file(logger, config_file_obj=json_file)
    """
    # Read Modbus TCP/RTU Master Configuration
    filename = 'resources/config-modbus-master.json'
    modbus_tcp_master, modbus_rtu_master = read_modbus_master_config(filename)
    """
     # Read Modbus TCP/RTU Master Configuration
    filename = 'resources/config-modbus-master.json'
    modbus_tcp_master, modbus_rtu_master = read_modbus_master_config(
        os.path.join(abs_path, filename))
  
    # Get modbus tcp master configuration only when enable flag is True
    # to establish connection to modbus tcp slave
    if modbus_tcp_master["enable"] == True:

        device_name = modbus_tcp_master["device_name"]
        slave_port = modbus_tcp_master["slave_port"]
        slave_ip = modbus_tcp_master["slave_ip"]
        slave_id = modbus_tcp_master["slave_id"]
        modbus_template_name = modbus_tcp_master["modbus_template"]
        polling_interval = modbus_tcp_master["polling_interval_sec"]
        
        # Initialize connection for modbus TCP based devices
        # Note: For MVP only single modbus TCP master is possible
        tcphandler = TCPConnectionHandler()
        tcphandler.init_modbus_tcp(slave_ip, slave_port)
        connection_status_tcp = tcphandler.connect()
        if connection_status_tcp is True:
            logger.info("Modbus TCP Master Connected to Slave: {}".format(slave_ip))
        else:
            logger.error("Failed to Connect Modbus TCP Slave: {}".format(slave_ip))
            #sys.exit()
              
    elif modbus_rtu_master["enable"] == True:
    
        device_name = modbus_rtu_master["device_name"]
        method = modbus_rtu_master["method"]
        baudrate = modbus_rtu_master["baudrate"]
        port = modbus_rtu_master["port"]
        port_mode = modbus_rtu_master["port_mode"]
        request_timeout = modbus_rtu_master["request_timeout"]
        stop_bits = modbus_rtu_master["stop_bits"]
        parity = modbus_rtu_master["parity"]
        polling_interval = modbus_rtu_master["polling_interval_sec"]
        modbus_template_name = modbus_rtu_master["modbus_template"]
        
        rtuhandler = SerialConnectionHandler(method, port, request_timeout, baudrate, device_name)
        rtuhandler.configure_serial_io(port, port_mode)
        rtuhandler.init_modbus_serial()
        connection_status_rtu = rtuhandler.connect()
       
    else:
        logger.warning("Modbus Master is Disabled in Configuration")

    # Get modbus command of the device tenmplate assigned to the modbus master
    # filename = 'resources/modbus_templates/ioLogik-E1242.json'
    filename = 'resources/modbus_templates/' + modbus_template_name
    template = read_ext_config(os.path.join(abs_path,filename))
    name, modbus_tags = parse_modbus_template(template)
    logger.debug("modbus tag: {}".format(modbus_tags))
    # name can be used as additional metadata in payload

    #Initialize queue object
    modbus_response_deque= deque(maxlen=100)
   
    
    try:
        if modbus_tcp_master["enable"] == True:
            ModbusTCPThread = threading.Thread(target=read_modbus_tcp_loop, args=(modbus_tags, connection_status_tcp, slave_ip, polling_interval, modbus_response_deque, tcphandler,))
            ModbusTCPThread.start()
            logger.info("************************")
            logger.info("Modbus TCP Master Thread Started!")
            logger.info("************************")
            
        elif modbus_rtu_master["enable"] == True:
        
            ModbusRTUThread = threading.Thread(target=read_modbus_rtu_loop, args=(modbus_tags, connection_status_rtu, device_name, polling_interval, modbus_response_deque, rtuhandler,))
            ModbusRTUThread.start()
            logger.info("************************")
            logger.info("Modbus RTU Master Thread Started!")
            logger.info("************************")
            
        mqttThread = threading.Thread(target=publish_mqtt, args=(mqtt, device_name, modbus_response_deque, modbus_tcp_master, modbus_rtu_master))
        mqttThread.start()
        logger.info("***************************")
        logger.info("Modbus to MQTT Thread Started!")
        logger.info("***************************")
        
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        # Clean up the connection
        ModbusTCPThread.join()
        ModbusRTUThread.join()
        mqttThread.join()
        sys.exit(0)
    

if __name__ == '__main__':
    main()

