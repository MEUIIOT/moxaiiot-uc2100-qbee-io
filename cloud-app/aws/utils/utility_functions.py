
import json 
import logging 

logger = logging.getLogger(__name__)

def read_ext_config(filename):
    """
    Configuration
    """
    try:
        with open(filename) as json_data_file:
            cfg_obj = json.load(json_data_file)
            logger.debug("Read External Config: {}".format(cfg_obj)) 
            return cfg_obj
    except IOError as e:
        logger.error(e)


def point_slope(INPUT, sourceMin, sourceMax, targetMin, targetMax):
    # Calculate Point Slope as in ThingsPro Gateway
    # Point-slope: OUTPUT = ((INPUT-sourceMin) * (targetMax-targetMin) / (sourceMax-sourceMin)) + targetMin
    OUTPUT = ((INPUT-sourceMin) * (targetMax-targetMin) / (sourceMax-sourceMin)) + targetMin
    return OUTPUT
    

def read_modbus_master_config(filename):
    config_modbus = read_ext_config(filename)
    if config_modbus["modbusTCP"]:
       modbus_tcp_master = config_modbus["modbusTCP"]
       logger.debug("modbusTCP: {}".format(modbus_tcp_master))
    else:
        logger.error("invalid modbus tcp master configuration")
        return 
    if config_modbus["modbusRTU"]:
       modbus_rtu_master = config_modbus["modbusRTU"]
       logger.debug("modbusRTU: {}".format(modbus_rtu_master)) 
    else:
        logger.error("invalid modbus rtu configuration")
        return 
    return modbus_tcp_master, modbus_rtu_master


def parse_modbus_template(modbus_template):
    """
    Example with the following modbus template 
    function check if keyword "name" and "tags" is in the json file 
    than it returns the object otheriwse, returns None    
    
    {
    "name": "PLC1",
    "tags": [
        {	
			"enable": true,
            "commandName": "oilTempC",
            "modbusDataType": "Int",
            "modbusFunction": "04-ReadInputRegisters",
            "address": 512, 
			"count": 1
        }
    }    
    """    
    if modbus_template["name"]: 
        get_name = modbus_template["name"]
        logger.debug("name: {}".format(get_name))
    if modbus_template["tags"]:
        modbus_tags = modbus_template["tags"]
        logger.debug("tags: {}".format(modbus_tags))
        return get_name, modbus_tags    


def get_tag_param(tag): 
    """
    function check if keyword "address", "count", "commandName", "modbusFunction", "modbusDataType" 
    is present in tag object than return tags value 
    """
    # parse tag information 
    address = tag["address"]
    count = tag["count"]
    commandName = tag["commandName"]
    modbusFunction = tag["modbusFunction"]
    modbusDataType = tag ["modbusDataType"]
    logger.debug("address: {}, count: {}, commandName: {}, modbusFunction: {}".format(address, count, commandName, modbusFunction)) 
    return address, count, commandName, modbusFunction, modbusDataType
   
   
def check_register_quantity(count, modbusFunction):
    """
    function to check count keyword in each modbus command configured in the template 
    when count value > 1 it generates the error. 
    otherwise function return count value

    The following condition trigger error with "count":2 
    {
    "name": "PLC1",
    "tags": [
        {	
			"enable": true,
            "commandName": "oilTempC",
            "modbusDataType": "Int",
            "modbusFunction": "04-ReadInputRegisters",
            "address": 512, 
			"count": 2
        }
    } 
    The current implementation doesn't allow to read contigous regerters in one command    
    """
    if count >1:
        logger.error("Requesting  multiple registers or coils in single command not implemented! FC: {}".format(modbusFunction))
        return False
    else:
        return count