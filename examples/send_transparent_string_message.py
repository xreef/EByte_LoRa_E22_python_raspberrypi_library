# Author: Renzo Mischianti
# Website: www.mischianti.org
#
# Description:
# This script demonstrates how to use the E22 LoRa module with RaspberryPi.
# Sending string
#
# Note: This code was written and tested using RaspberryPi on an ESP32 board.
#       It works with other boards, but you may need to change the UART pins.

import serial

from lora_e22 import LoRaE22, Configuration
from lora_e22_constants import RssiAmbientNoiseEnable, RssiEnableByte
from lora_e22_operation_constant import ResponseStatusCode

# Initialize the LoRaE22 module
loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
lora = LoRaE22('400T22D', loraSerial, aux_pin=18, m0_pin=23, m1_pin=24)
code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

# Set the configuration to default values and print the updated configuration to the console
# Not needed if already configured
configuration_to_set = Configuration('400T22D')
# To enable RSSI, you must also enable RSSI on receiver
configuration_to_set.TRANSMISSION_MODE.enableRSSI = RssiEnableByte.RSSI_ENABLED
code, confSetted = lora.set_configuration(configuration_to_set)
print("Set configuration: {}", ResponseStatusCode.get_description(code))

# Send a string message (transparent)
message = 'Hello, world!'
code = lora.send_transparent_message(message)
print("Send message: {}", ResponseStatusCode.get_description(code))
