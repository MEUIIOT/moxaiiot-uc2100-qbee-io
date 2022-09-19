# Template name rules

Templates taken from the "ioLogik" folder inside the "modbus_templates" folder must be defined in the "config-modbus-master.json" file with the following name:

"ioLogik/template_name_required_by_you.json". 

The "command name" of registers follows the following format:
"type_access_count". Here the type can be rtdi, ro, ai (analog input), ao (analog output), di (digital input) and do (digital output). The access can be r (read) or w (write). For a memory with count as "Length", the count is the number used to uniquely identify that register and can have values ranging from 0 to "Length-1".