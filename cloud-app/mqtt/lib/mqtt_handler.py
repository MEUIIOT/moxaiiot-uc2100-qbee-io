#!/usr/bin/env python 3
"""
MQTT client base class to Connect, Publish and Subscribe messages using Mosquitto broker  
"""

import time
import json
import ssl
import sys
import logging
import paho.mqtt.client as mqtt_client
   
logger = logging.getLogger(__name__)

class MqttBaseCLass():
 
    def __init__(self, **kwargs):
        
        self._ext_conf = kwargs.get('conf', None)
        
        self._client = None
        self._userdata = None
        self._mqqtconnect = None
        self.IS_CONNECTED = False
        
        self._broker_url = "127.0.0.1"
        self._port = 1883
        self._clean_session = True
        self._keep_alive_sec = 60
        self._topic = None
        self._publish_interval = 1
        self._subscribe_interval = 1 
        self.parse_configuration()
        
    def parse_configuration(self):
        """
        Parse config.json file 
        """
        if not self._ext_conf:
            logger.error('Empty configuration!')
            return False          
        try:
            # continue here 
            if self._ext_conf["general"]["broker"]: 
                self._broker_url = self._ext_conf["general"]["broker"] 
                logger.debug("broker: {}".format(self._broker_url))
            
            if self._ext_conf["general"]["port"]: 
                self._port = self._ext_conf["general"]["port"] 
                logger.debug("port: {}".format(self._port))    
         
            if self._ext_conf["general"]['clean_session']:
                self._clean_session = self._ext_conf["general"]['clean_session']
                logger.debug("clean_session: {}".format(self._clean_session))
                
            if self._ext_conf["general"]['keep_alive_sec']:
                self._broker_keepalive = self._ext_conf["general"]['keep_alive_sec'] 
                logger.debug("keep_alive_sec: {}".format(self._broker_keepalive))
                
            if self._ext_conf["general"]['topic']:
                self._topic = self._ext_conf["general"]['topic'] 
                logger.debug("topic: {}".format(self._topic))
                   
            if self._ext_conf["general"]['publish_interval']:
                self._publish_interval = self._ext_conf["general"]['publish_interval'] 
                logger.debug("publish_interval: {}".format(self._publish_interval)) 
           
            if self._ext_conf["general"]['subscribe_interval']:
                self._subscribe_interval = self._ext_conf["general"]['subscribe_interval'] 
                logger.debug("subscribe_interval: {}".format(self._subscribe_interval))        
            
        except KeyError as error:
            logger.warning("{} does not existing in configuration file".format(error)) 
           
        logger.info("Parse Configuration Successfull! ")
        return True 


    def init_mqtt_client(self):
        """
        Initilaize mqtt client configuration
        """
        logger.info("Create MQTT Client {}".format(self._clean_session))
        self._client = mqtt_client.Client(clean_session= self._clean_session, userdata=self._userdata)
        
        logger.info('Register Callback functions')
        
        self._client.on_connect = self.on_connect_callback
        self._client.on_disconnect = self.on_disconnect_callback
        self._client.on_publish = self.on_publish_callback
        self._client.on_message = self.on_message_callback
        self._client.on_subscribe = self.on_subscribe_callback
        self._client.on_log = self.on_log
        
        self._client.loop_start()
        return True
        
    def connect_mqtt_broker(self):
        """
        Initilaize request for connecting to the MQTT Broker
        """       
        self._mqqtconnect = self._client.connect(host= self._broker_url, port= self._port, keepalive= self._keep_alive_sec)
        logger.info("Connecting to broker: {}".format(self._broker_url))
        
    def on_connect_callback(self, client, userdata, flags, rc):
        """
        This function is called when client is connected to MQTT Broker
        """     
        logger.info('OnConnect! rc={}, flags={}'.format(rc, flags))     
        if rc == 0:           
            self.IS_CONNECTED = True
            logger.info("*************************************************************")
            logger.info("Connected successfully to broker: {}".format(self._broker_url))
            logger.info("*************************************************************")
            
        elif rc == 1:
            logger.error("Connection refused - incorrect protocol version, result code: {}".format(rc)) 
            self._client.loop_stop()
               
        elif rc == 2:
            logger.error("Connection refused - invalid client identifier, result code: {}".format(rc)) 
            self._client.loop_stop() 
             
        elif rc == 3:
            logger.error("Connection refused - server unavailable, result code: {}".format(rc)) 
            self._client.loop_stop()
            
        elif rc == 4:
            logger.error("Connection refused - bad username or password, result code: {}".format(rc))
            self._client.loop_stop()
            
        else:
            logger.error("Connection refused - not authorised, result code: {}".format(rc)) 
            self._client.loop_stop()
               
    def on_disconnect_callback(self, client, userdata, rc):
        """
        This function is called when client is disconnected from MQTT Broker
        """
        
        logger.info('OnDisonnect! rc = %s', rc)
        self.IS_CONNECTED = False
        if rc:
            logger.error('Disonnected with result code = {}'.format(rc))  
        return

    def on_log(self, client, userdata, level, buf):
        logger.debug("OnLog(%s): %s ", level, buf)
        return
        
    def on_publish_callback(self, client, userdata, mid):
        """
        This function is called when message is publish to MQTT Broker
        """
        logger.debug('OnPublish MsgID [%s]', mid)
        
    def on_subscribe_callback(self, client, obj, mid, granted_qos):
        logger.debug("Subscribed: " + str(mid) + " " + str(granted_qos))
        
    def on_message_callback(self, client, obj, message):
        #logger.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        payload = str(message.payload.decode("utf-8"))
        logger.debug("Received message '{}' on topic '{}' with Qos {}".format(
            payload, message.topic, str(message.qos)
        ))
        
    def is_open(self):
        """
        To check existing client connection to MQTT Broker
        """
        if self._client and self.IS_CONNECTED == True:
            return True
        else:
            return False
