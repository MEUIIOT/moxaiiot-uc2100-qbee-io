
import logging 
import sys 
import os 
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

logger = logging.getLogger(__name__)



class SerialConnectionHandler:
    
    def __init__(self, method, port, timeout, baudrate, device_name):
    
        self.IS_CONNECTED = False
        self.serial_connection = None    
        
        self.method = method
        self.port = port
        self.timeout = timeout
        self.baudrate = baudrate        
        self.device_name = device_name     
        
    def init_modbus_serial(self):
        self.serial_connection = ModbusClient(method=self.method, port=self.port, timeout=self.timeout,
                           baudrate=self.baudrate)
        return self.serial_connection
    
    def connect(self):
    
        output = self.serial_connection.connect()
        if output is True:
            self.IS_CONNECTED = True
            logger.info("*************************************************************")
            logger.info("Connected successfully to Modbus RTU Slave: {}".format(self.device_name))
            logger.info("*************************************************************")
            return True
        else:
            logger.error("Serial connection closed!")
            return False

    def close(self):
        self.serial_connection.close()
        logger.info("Serial connection closed successfully: {}".format(self.serial_connection))

    @staticmethod
    def configure_serial_io(port, mode):
        logger.info("***************************************************")
        logger.info("Calling mx-uart-ctl tool to change serial port mode")
        logger.info("***************************************************")
        
        # Convert pyserial port names into mx-uart-ctl tool port numbers
        if port == "/dev/ttyM0":
            port = 0
        elif port == "/dev/ttyM1":
            port = 1
        else:
            logger.error("Invalid serial port name:{}".format(port))
            sys.exit()

        if mode == "RS232":
            # TODO: os.popen spawns a subshell, can be replaced by subprocess.Popen or subprocess.run
            stream = os.popen('sudo mx-uart-ctl -p' + str(port) + ' -m 0')
        elif mode == "RS485-2W":
            stream = os.popen('sudo mx-uart-ctl -p' + str(port) + ' -m 1')
        elif mode == "RS485-4W" or mode == "RS422":
            stream = os.popen('sudo mx-uart-ctl -p' + str(port) + ' -m 2')
        else:
            logger.error("Invalid port mode:{}".format(mode))
            sys.exit()

        output = stream.read()
        logger.info(output)
