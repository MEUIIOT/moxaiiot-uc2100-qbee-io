import sys
import time
import json 
import logging 
import threading

from collections import deque

#from pymodbus.payload import BinaryPayloadDecoder

from lib.mqtt_handler import MqttBaseCLass
from lib.tcp_handler import TCPConnectionHandler
from lib.serial_handler import SerialConnectionHandler
from lib.modbus_master import send_modbus_request, recv_modbus_msg

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


def build_payload(device_name, modbus_response_deque):
    if len(modbus_response_deque) != 0:    
        # add provider name tcp or rtu 
        payload = modbus_response_deque.popleft()
        # Add additional info modbus deviceName and prvdName in the payload received via queue  
        payload["prvdName"] = "modbus_tcp_master" # static needs to be added dynamically in case modbus rtu device is also enable
        payload["deviceName"] = device_name    
        return json.dumps(payload)
        

def publish_mqtt(mqtt, device_name, modbus_response_deque):
    while True:
        # Publish to MQTT broker 
        payload = build_payload(device_name, modbus_response_deque)
        modbus_to_mqtt(mqtt, payload)

def main():
    
    # Read configuretaion file into python object 
    config_mqtt_broker = read_ext_config('resources/config-internal-broker.json')
    
    ## Initialize MQTT
    mqtt = MqttBaseCLass(conf = config_mqtt_broker)
    mqtt.init_mqtt_client()
    mqtt.connect_mqtt_broker()
       
    # Config logging for console output 
    filename = 'resources/config-modbus-master.json' 
    json_file = read_ext_config(filename)
    update_logger_verbose_level_from_config_file(logger, config_file_obj=json_file)
    
    # Read Modbus TCP/RTU Master Configuration 
    filename = 'resources/config-modbus-master.json'       
    modbus_tcp_master, modbus_rtu_master = read_modbus_master_config(filename)
  
    # Initialize connection for modbus TCP based devices 
    # Note: For MVP only single modbus TCP master is possible  
    tcphandler = TCPConnectionHandler()
  
    # Get modbus tcp master configuration only when enable flag is True 
    # to establish connection to modbus tcp slave 
    if modbus_tcp_master["enable"] == True: 
        
        device_name = modbus_tcp_master["device_name"]
        slave_port = modbus_tcp_master["slave_port"]
        slave_ip = modbus_tcp_master["slave_ip"]
        slave_id = modbus_tcp_master["slave_id"]
        modbus_template_name = modbus_tcp_master["modbus_template"]
        polling_interval = modbus_tcp_master["polling_interval_sec"]
        
        tcphandler.init_modbus_tcp(slave_ip, slave_port)
        connection_status_tcp = tcphandler.connect()
        if connection_status_tcp is True:
            logger.info("Modbus TCP Master Connected to Slave: {}".format(slave_ip))
        else:
            logger.error("Failed to Connect Modbus TCP Slave: {}".format(slave_ip))
            #sys.exit()
            
    elif modbus_rtu_master["enable"] == True: 
        logger.error("Not Implemented")
    else:
        logger.warning("Modbus TCP Master is Disabled with Device Name: {}".format(device_name))
   
    # Get modbus command of the device tenmplate assigned to the modbus master  
    # filename = 'resources/modbus_templates/ioLogik-E1242.json'   
    filename = 'resources/modbus_templates/' + modbus_template_name   
    template = read_ext_config(filename)
    name, modbus_tags = parse_modbus_template(template) 
    # name can be used as additional metadata in payload
    
    #Initialize queue object
    modbus_response_deque= deque(maxlen=100)
    
    try:     
        recvModbusThread = threading.Thread(target=recv_modbus_msg, args=(modbus_tags, connection_status_tcp, slave_ip, polling_interval, modbus_response_deque, tcphandler,))
        recvModbusThread.start()
        logger.info("************************")
        logger.info("Recv Modbus Thread Started!")
        logger.info("************************")
        
        mqttThread = threading.Thread(target=publish_mqtt, args=(mqtt, device_name, modbus_response_deque,))
        mqttThread.start()
        logger.info("***************************")
        logger.info("Modbus to MQTT Thread Started!")
        logger.info("***************************")
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        # Clean up the connection
        recvModbusThread.join()
        mqttThread.join()
        sys.exit(0)       
    

if __name__ == '__main__':
    main()
    
