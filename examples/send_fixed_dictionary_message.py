# Author: Renzo Mischianti
# Website: www.mischianti.org
#
# Description:
# This script demonstrates how to use the E22 LoRa module with RaspberryPi.
# Sending dictionary to a specified address (receiver)
# ADDH = 0x00
# ADDL = 0x02
# CHAN = 23
#
# Note: This code was written and tested using RaspberryPi on an ESP32 board.
#       It works with other boards, but you may need to change the UART pins.

import serial

from lora_e22 import LoRaE22, Configuration
from lora_e22_constants import FixedTransmission, RssiEnableByte
from lora_e22_operation_constant import ResponseStatusCode

# Initialize the LoRaE22 module
loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
lora = LoRaE22('400T22D', loraSerial, aux_pin=18, m0_pin=23, m1_pin=24)
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('400T22D')
configuration_to_set.ADDL = 0x02 # Address of this sender no receiver
configuration_to_set.TRANSMISSION_MODE.fixedTransmission = FixedTransmission.FIXED_TRANSMISSION
# To enable RSSI, you must also enable RSSI on receiver
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED

code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}", ResponseStatusCode.get_description(code))

# Send a dictionary message (fixed)
data = {'key1': 'value1', 'key2': 'value2'}
code = lora.send_fixed_dict(0, 0x01, 23, data)
# The receiver must be configured with ADDH = 0x00, ADDL = 0x01, CHAN = 23
print("Send message: {}", ResponseStatusCode.get_description(code))
