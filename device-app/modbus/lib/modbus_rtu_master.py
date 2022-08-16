
import time 
import logging 

from utils.utility_functions import point_slope, get_tag_param, check_register_quantity

logger = logging.getLogger(__name__)


def read_modbus_rtu_data(tag,  modbus_response_deque, rtuHandler):     
    address, count, commandName, modbusFunction, modbusDataType = get_tag_param(tag)
    logger.debug("address: {}, count: {}, commandName: {}, modbusFunction: {}".format(address, count, commandName, modbusFunction)) 

    message = {"modbusFC": "", "tagName": "", "tagValue": "", "ts": ""}

    if modbusFunction == "01-ReadCoils":
        count = check_register_quantity(count, modbusFunction)     
        if count is not False:    
            ## ToDo
            # Map coil address to their corresponding coil value when requesting multiple bits in single command 
            
            #logger.info("****************** 01-ReadCoils ************************")
            response = rtuHandler.serial_connection.read_coils(address,count,unit=1)
            logger.info("[RECV] Modbus RTU respone FC:{} {}: {}".format(modbusFunction, commandName, response.bits[0]))
            
            message["modbusFC"] = modbusFunction
            message["tagName"] = commandName
            message["tagValue"] = response.bits[0]
            message["ts"] = int(time.time()*1000) 
            
            modbus_response_deque.append(message)
            
            # function return 1 byte with padded zero in the end 
            # example: read single bit with address = 0, count= 1 function return single byte with padded zero "10000000"
        
    if modbusFunction == "02-ReadDiscreteInputs":
        ## ToDo
        # Map coil address to their corresponding coil value when requesting multiple bits in single command 
        
        #logger.info("****************** 02-ReadDiscreteInputs ************************")
        response = rtuHandler.serial_connection.read_discrete_inputs(address, count, unit=1)
        logger.info("[RECV] Modbus RTU respone FC:{} {}: {}".format(modbusFunction, commandName, response.bits[0]))
        
        message["modbusFC"] = modbusFunction
        message["tagName"] = commandName
        message["tagValue"] = response.bits[0]
        message["ts"] = int(time.time()*1000) 
        
        modbus_response_deque.append(message)
        
    if modbusFunction == "03-ReadHoldingRegisters":
        count = check_register_quantity(count, modbusFunction)   
        if count is not False:  
            try:
                
                #logger.info("****************** 03-ReadHoldingRegisters ************************")
                ## Test Read Holding Register
                response = rtuHandler.serial_connection.read_holding_registers(address, count,unit=1)
                # return list of registers with size 1 
                logger.info("[RECV] Modbus RTU respone FC:{} {}: {}".format(modbusFunction, commandName, response.registers[0]))
                
                message["modbusFC"] = modbusFunction
                message["tagName"] = commandName
                message["tagValue"] = response.registers[0]
                message["ts"] = int(time.time()*1000) 
            
                modbus_response_deque.append(message)
                
                # scale down original value
                motorCurrent = point_slope(response.registers[0], 0, 1000, 0, 10)
                logger.debug("motorCurrent: {} scale down by calculating point slope".format(motorCurrent))
              
            except AttributeError as e:
                logger.error("{}: Command Failed! The requested register not available on modbus slave with FC: {}".format(commandName, modbusFunction))
            
        
    if modbusFunction == "04-ReadInputRegisters":  
        count = check_register_quantity(count, modbusFunction) 
        if count is not False:  
            ## ToDo
            # Map register address to their corresponding register value when requesting multiple regsiters in single command 
            
            #logger.info("****************** 04-ReadInputRegisters ************************")
            logger.debug("address: {}, count: {}, commandName: {}, modbusFunction: {}".format(address, count, commandName, modbusFunction)) 
            ## Test Read Input Register
            response = rtuHandler.serial_connection.read_input_registers(address,count,unit=1) 
            
            logger.info("[RECV] Modbus RTU respone FC:{} {}: {}".format(modbusFunction, commandName, response.registers[0]))
            
            message["modbusFC"] = modbusFunction
            message["tagName"] = commandName
            message["tagValue"] = response.registers[0]
            message["ts"] = int(time.time()*1000) 

            modbus_response_deque.append(message)

            # scale down original value 
            oilTempC  = point_slope(response.registers[0], 0, 65535, 0, 100)
            logger.debug("oilTemp: {} scale down by calculating point slope".format(oilTempC))
            
def read_modbus_rtu_loop(modbus_tags, connection_status_rtu, device_name, polling_interval, modbus_response_deque, rtuHandler):
    try:
        while True:
            for tag in modbus_tags:
                # filter commands on enable flag is True 
                if tag["enable"] == True: 
                    if connection_status_rtu is True:
                        logger.debug("[OPEN] Modbus RTU Master Connected with : {}".format(device_name))
                        read_modbus_rtu_data(tag,  modbus_response_deque, rtuHandler)
                        logger.debug("[SEND] Modbus RTU request to Slave : {}".format(device_name))
                    else:
                        logger.error("Failed to Connect Modbus RTU Slave: {}".format(device_name))    
            time.sleep(polling_interval)
            logger.debug("modbus_response_deque length:", len(modbus_response_deque))
             
    except KeyboardInterrupt:
        rtuHandler.close()
