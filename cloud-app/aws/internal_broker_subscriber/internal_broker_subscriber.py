import logging
import time 
from collections import deque
import paho.mqtt.client as mqtt

class MosquittoMQTTSubscriber:

    def __init__(self, logger, cloud_mqtt_broker_queue, topic="modbus/mqtt/telemetry", host="127.0.0.1", port=1883):
        
        self.logger = logger

        self.cloud_mqtt_broker_queue = cloud_mqtt_broker_queue

        self._topic = topic 

        self.client = mqtt.Client()

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log

        self.client.connect(host, port, 60)

    def _error_str(self, rc):
        """
        Convert a Paho error to a human readable string.
        """
        return "{}: {}".format(rc, mqtt.error_string(rc))

    def _on_connect(self, client, user_data, flags, rc):
        self.logger.debug("on_connect: {}".format(mqtt.connack_string(rc)))
        self.logger.info("Subscribing to the internal broker")
        client.subscribe(self._topic, 0)

    def _on_disconnect(self, client, user_data, flags, rc):
        self.logger.debug("on_disconnect: {}".format(self._error_str(rc)))

    def _on_publish(self, client, user_data, mid):
        self.logger.debug("on_publish: {}".format(mid))

    def _on_subscribe(self, client, user_data, mid, granted_qos):
        self.logger.debug("on_subscribed: " + str(mid) + " " + str(granted_qos)) 
        
    def _on_message(self, client, user_data, message):
        payload = str(message.payload.decode("utf-8"))
        self.logger.info("[Received message] '{}' on topic '{}' with Qos {}".format(
            payload, message.topic, str(message.qos)
        ))
        self.cloud_mqtt_broker_queue.append(message.payload.decode("utf-8"))

    def _on_log(self, client, user_data, level, buf):
        self.logger.debug("on_log: (%s) - %s ", level, buf)

    def run(self):
        self.client.loop_start()



def main():
    logger = logging.getLogger(__name__)
    messages_queue = deque(maxlen=100)
    
    int_broker_subscriber = MosquittoMQTTSubscriber(logger, messages_queue)
    int_broker_subscriber.run()
  
if __name__ == "__main__":
    main()
