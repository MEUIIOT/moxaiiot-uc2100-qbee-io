
import logging 
from pymodbus.client.sync import ModbusTcpClient as TcpClient

logger = logging.getLogger(__name__)


class TCPConnectionHandler:

    def __init__(self):
    
        self.IS_CONNECTED = False
        self.tcp_connection = None  
    
    def init_modbus_tcp(self, host, port):
        self.tcp_connection = TcpClient(host, port) 
        return self.tcp_connection
    
    def connect(self):
    
        status = self.tcp_connection.connect()
        if status is True:
            self.IS_CONNECTED = True
            logger.info("*************************************************************")
            logger.info("Connected successfully to Modbus TCP Slave: {}".format(self.tcp_connection))
            logger.info("*************************************************************")
            return True
        else:
            logger.error("TCP connection closed!")
            return False
            
    def close(self):
        self.IS_CONNECTED = False
        self.tcp_connection.close()
        logger.info("TCP connection closed successfully: {}".format(self.tcp_connection))
            
