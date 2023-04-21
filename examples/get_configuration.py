# Author: Renzo Mischianti
# Website: www.mischianti.org
#
# Description:
# This script initializes the E22 LoRa module with RaspberryPi,
# retrieves the current configuration, and prints it to the console.
# The code demonstrates how to use the LoRaE22 library to interact with the module and read its configuration.
#
# Note: This code was written and tested using RaspberryPi on an ESP32 board.
#       It works with other boards, but you may need to change the UART pins.


import serial

from lora_e22 import LoRaE22, print_configuration
from lora_e22_operation_constant import ResponseStatusCode

loraSerial = serial.Serial('/dev/serial0') #, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

lora = LoRaE22('400T22D', loraSerial, aux_pin=18, m0_pin=23, m1_pin=24)

code = lora.begin()
print("Initialization: {}", ResponseStatusCode.get_description(code))

code, configuration = lora.get_configuration()

print("Retrieve configuration: {}", ResponseStatusCode.get_description(code))

print_configuration(configuration)

# Retrieve configuration: {} Success
# ----------------------------------------
# HEAD :  0xc1   0x0   0x9
#
# AddH :  0x0
# AddL :  0x0
#
# Chan :  23  ->  433
#
# SpeedParityBit :  0b0  ->  8N1 (Default)
# SpeedUARTDatte :  0b11  ->  9600bps (default)
# SpeedAirDataRate :  0b10  ->  2.4kbps (default)
#
# OptionSubPacketSett:  0b0  ->  240bytes (default)
# OptionTranPower :  0b0  ->  22dBm (Default)
# OptionRSSIAmbientNo:  0b0  ->  Disabled (default)
#
# TransModeWORPeriod :  0b11  ->  2000ms (default)
# TransModeTransContr:  0b0  ->  WOR Receiver (default)
# TransModeEnableLBT :  0b0  ->  Disabled (default)
# TransModeEnableRSSI:  0b0  ->  Disabled (default)
# TransModeEnabRepeat:  0b0  ->  Disabled (default)
# TransModeFixedTrans:  0b0  ->  Transparent transmission (default)
# ----------------------------------------
