#############################################################################################
# EBYTE LoRa E22 Series for RaspberryPi
#
# AUTHOR:  Renzo Mischianti
# VERSION: 0.0.1
#
# This library is based on the work of:
# https://www.mischianti.org/category/my-libraries/lora-e22-devices/
#
# This library implements the EBYTE LoRa E22 Series for RaspberryPi.
#
#  ____________________________________________
# |          3V3 | 1     2 | 5V                |
# |        GPIO2 | 3     4 | 5V                |
# |        GPIO3 | 5     6 | GND               |
# |        GPIO4 | 7     8 | GPIO14 (TX)       |
# |          GND | 9    10 | GPIO15 (RX)       |
# |       GPIO17 |11    12 | GPIO18 AUX        |
# |       GPIO27 |13    14 | GND               |
# |       GPIO22 |15    16 | GPIO23 M0         |
# |          3V3 |17    18 | GPIO24 M1         |
# |       GPIO10 |19    20 | GND               |
# |        GPIO9 |21    22 | GPIO25            |
# |       GPIO11 |23    24 | GPIO8             |
# |          GND |25    26 | GPIO7             |
# |       GPIO0  |27    28 | GPIO1             |
# |       GPIO5  |29    30 | GND               |
# |       GPIO6  |31    32 | GPIO12            |
# |      GPIO13  |33    34 | GND               |
# |      GPIO19  |35    36 | GPIO16            |
# |          3V3 |37    38 | GPIO26            |
# |      GPIO20  |39    40 | GND               |
#  --------------------------------------------
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Renzo Mischianti www.mischianti.org All right reserved.
#
# You may copy, alter and reuse this code in any way you like, but please leave
# reference to www.mischianti.org in your comments if you redistribute this code.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#############################################################################################

from lora_e22_constants import UARTParity, UARTBaudRate, TransmissionPower, FixedTransmission, AirDataRate, \
    OperatingFrequency, LbtEnableByte, WorPeriod, RssiEnableByte, RssiAmbientNoiseEnable, SubPacketSetting
from lora_e22_operation_constant import ResponseStatusCode, SerialUARTBaudRate, \
    PacketLength, RegisterAddress

import re
import time
import json
from RPi import GPIO

from lora_e22_constants import WorTransceiverControl, RepeaterModeEnableByte
from lora_e22_operation_constant import ModeType, ProgramCommand


class Logger:
    def __init__(self, enable_debug):
        self.enable_debug = enable_debug
        self.name = ''

    def debug(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' DEBUG ', msg, *args)

    def info(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' INFO ', msg, *args)

    def error(self, msg, *args):
        if self.enable_debug:
            print(self.name, ' ERROR ', msg, *args)

    def getLogger(self, name):
        self.name = name
        return Logger(self.enable_debug)


logging = Logger(False)

logger = logging.getLogger(__name__)

BROADCAST_ADDRESS = 0xFF


class Speed:
    def __init__(self, model):
        self.model = model

        self.airDataRate = AirDataRate.AIR_DATA_RATE_010_24
        self.uartBaudRate = UARTBaudRate.BPS_9600
        self.uartParity = UARTParity.MODE_00_8N1

    def get_air_data_rate(self):
        return AirDataRate.get_description(self.airDataRate)

    def get_UART_baud_rate(self):
        return UARTBaudRate.get_description(self.uartBaudRate)

    def get_UART_parity_description(self):
        return UARTParity.get_description(self.uartParity)


class TransmissionMode:
    def __init__(self, model):
        self.model = model

        self.WORPeriod = WorPeriod.WOR_2000_011
        self.WORTransceiverControl = WorTransceiverControl.WOR_RECEIVER
        self.enableLBT = LbtEnableByte.LBT_DISABLED
        self.enableRepeater = RepeaterModeEnableByte.REPEATER_DISABLED
        self.fixedTransmission = FixedTransmission.TRANSPARENT_TRANSMISSION
        self.enableRSSI = RssiEnableByte.RSSI_DISABLED

    def get_WOR_period_description(self):
        return WorPeriod.get_description(self.WORPeriod)

    def get_LBT_enable_byte_description(self):
        return LbtEnableByte.get_description(self.enableLBT)

    def get_fixed_transmission_description(self):
        return FixedTransmission.get_description(self.fixedTransmission)

    def get_RSSI_enable_byte_description(self):
        return RssiEnableByte.get_description(self.enableRSSI)

    def get_WOR_transceiver_control_description(self):
        return WorTransceiverControl.get_description(self.WORTransceiverControl)

    def get_repeater_mode_enable_byte_description(self):
        return RepeaterModeEnableByte.get_description(self.enableRepeater)


class Option:
    def __init__(self, model):
        self.model = model

        self.transmissionPower = TransmissionPower(self.model).get_transmission_power().get_default_value()
        self.reserved = 0
        self.RSSIAmbientNoise = RssiAmbientNoiseEnable.RSSI_AMBIENT_NOISE_DISABLED
        self.subPacketSetting = SubPacketSetting.SPS_240_00

    def get_transmission_power_description(self):
        return TransmissionPower(self.model).get_transmission_power_description(self.transmissionPower)

    def get_RSSI_ambient_noise_enable(self):
        return RssiAmbientNoiseEnable.get_description(self.RSSIAmbientNoise)

    def get_sub_packet_setting(self):
        return SubPacketSetting.get_description(self.subPacketSetting)


class Crypt:
    def __init__(self):
        self.CRYPT_H = 0
        self.CRYPT_L = 0


class Configuration:
    def __init__(self, model):
        self.model = model

        self.package_type = None
        self.frequency = None
        self.transmission_power = None

        if model is not None:
            self.package_type = model[6]
            self.frequency = int(model[0:3])
            self.transmission_power = int(model[4:6])

        self._COMMAND = 0
        self._STARTING_ADDRESS = 0
        self._LENGTH = 0
        self.ADDH = 0
        self.ADDL = 0
        self.NETID = 0

        self.SPED = Speed(self.model)
        self.OPTION = Option(self.model)
        self.CHAN = 23
        self.TRANSMISSION_MODE = TransmissionMode(self.model)
        self.CRYPT = Crypt()

    def get_model(self):
        return self.model

    def get_package_type(self):
        return self.package_type

    def get_channel(self):
        return self.CHAN

    def get_frequency(self):
        return OperatingFrequency.get_freq_from_channel(self.frequency, self.CHAN)

    def get_model(self):
        return self.model

    def to_hex_string(self):
        return ''.join(['0x{:02X} '.format(x) for x in self.to_hex_array()])

    def to_bytes(self):
        hexarray = self.to_hex_array()
        # Convert values to valid byte values
        for i in range(len(hexarray)):
            if hexarray[i] > 255:
                hexarray[i] = hexarray[i] % 256

        return bytes(hexarray)

    def from_hex_array(self, hex_array):
        self._COMMAND = hex_array[0]
        self._STARTING_ADDRESS = hex_array[1]
        self._LENGTH = hex_array[2]
        self.ADDH = hex_array[3]
        self.ADDL = hex_array[4]
        self.NETID = hex_array[5]

        self.SPED.airDataRate = hex_array[6] & 0b00000111
        self.SPED.uartParity = (hex_array[6] & 0b00011000) >> 3
        self.SPED.uartBaudRate = (hex_array[6] & 0b11100000) >> 5

        self.OPTION.transmissionPower = hex_array[7] & 0b00000011
        self.OPTION.RSSIAmbientNoise = (hex_array[7] & 0b00100000) >> 5
        self.OPTION.subPacketSetting = (hex_array[7] & 0b11000000) >> 6

        self.CHAN = hex_array[8]

        self.TRANSMISSION_MODE.WORPeriod = hex_array[9] & 0b00000111
        self.TRANSMISSION_MODE.WORTransceiverControl = (hex_array[9] & 0b00001000) >> 3
        self.TRANSMISSION_MODE.enableLBT = (hex_array[9] & 0b00010000) >> 4
        self.TRANSMISSION_MODE.enableRepeater = (hex_array[9] & 0b00100000) >> 5
        self.TRANSMISSION_MODE.fixedTransmission = (hex_array[9] & 0b01000000) >> 6
        self.TRANSMISSION_MODE.enableRSSI = (hex_array[9] & 0b10000000) >> 7

        self.CRYPT.CRYPT_H = hex_array[10]
        self.CRYPT.CRYPT_L = hex_array[11]

    def to_hex_array(self):
        return [self._COMMAND, self._STARTING_ADDRESS, self._LENGTH, self.ADDH, self.ADDL, self.NETID,
                self.SPED.airDataRate | (self.SPED.uartParity << 3) | (self.SPED.uartBaudRate << 5),
                self.OPTION.transmissionPower | (self.OPTION.RSSIAmbientNoise << 5) | (self.OPTION.subPacketSetting << 6),
                self.CHAN,
                self.TRANSMISSION_MODE.WORPeriod | (self.TRANSMISSION_MODE.WORTransceiverControl << 3) | (
                        self.TRANSMISSION_MODE.enableLBT << 4) | (self.TRANSMISSION_MODE.enableRepeater << 5) | (
                        self.TRANSMISSION_MODE.fixedTransmission << 6) | (self.TRANSMISSION_MODE.enableRSSI << 7),
                self.CRYPT.CRYPT_H, self.CRYPT.CRYPT_L]

    def from_hex_string(self, hex_string):
        self.from_hex_array([int(hex_string[i:i + 2], 16) for i in range(0, len(hex_string), 2)])

    def from_bytes(self, bytes):
        self.from_hex_array([x for x in bytes])


def print_configuration(configuration):
    print("----------------------------------------")
    print("HEAD : ", hex(configuration._COMMAND), " ", hex(configuration._STARTING_ADDRESS), " ",
          hex(configuration._LENGTH))
    print("")
    print("AddH : ", hex(configuration.ADDH))
    print("AddL : ", hex(configuration.ADDL))
    print("")
    print("Chan : ", str(configuration.CHAN), " -> ", configuration.get_frequency())
    print("")
    print("SpeedParityBit : ", bin(configuration.SPED.uartParity), " -> ",
          configuration.SPED.get_UART_parity_description())
    print("SpeedUARTDatte : ", bin(configuration.SPED.uartBaudRate), " -> ", configuration.SPED.get_UART_baud_rate())
    print("SpeedAirDataRate : ", bin(configuration.SPED.airDataRate), " -> ", configuration.SPED.get_air_data_rate())
    print("")
    print("OptionSubPacketSett: ", bin(configuration.OPTION.subPacketSetting), " -> ",
          configuration.OPTION.get_sub_packet_setting())
    print("OptionTranPower : ", bin(configuration.OPTION.transmissionPower), " -> ",
          configuration.OPTION.get_transmission_power_description())
    print("OptionRSSIAmbientNo: ", bin(configuration.OPTION.RSSIAmbientNoise), " -> ",
          configuration.OPTION.get_RSSI_ambient_noise_enable())
    print("")
    print("TransModeWORPeriod : ", bin(configuration.TRANSMISSION_MODE.WORPeriod), " -> ",
          configuration.TRANSMISSION_MODE.get_WOR_period_description())
    print("TransModeTransContr: ", bin(configuration.TRANSMISSION_MODE.WORTransceiverControl), " -> ",
          configuration.TRANSMISSION_MODE.get_WOR_transceiver_control_description())
    print("TransModeEnableLBT : ", bin(configuration.TRANSMISSION_MODE.enableLBT), " -> ",
          configuration.TRANSMISSION_MODE.get_LBT_enable_byte_description())
    print("TransModeEnableRSSI: ", bin(configuration.TRANSMISSION_MODE.enableRSSI), " -> ",
          configuration.TRANSMISSION_MODE.get_RSSI_enable_byte_description())
    print("TransModeEnabRepeat: ", bin(configuration.TRANSMISSION_MODE.enableRepeater), " -> ",
          configuration.TRANSMISSION_MODE.get_repeater_mode_enable_byte_description())
    print("TransModeFixedTrans: ", bin(configuration.TRANSMISSION_MODE.fixedTransmission), " -> ",
          configuration.TRANSMISSION_MODE.get_fixed_transmission_description())
    print("----------------------------------------")


MAX_SIZE_TX_PACKET = 240


class ModuleInformation:
    def __init__(self):
        self._COMMAND = 0
        self._STARTING_ADDRESS = 0
        self._LENGTH = 0
        self.reserved = [0, 0, 0]
        self.model = 0
        self.version = 0
        self.features = 0
        self.end = 0


    def to_hex_array(self):
        hex_array = []
        hex_array.append(self._COMMAND)
        hex_array.append(self._STARTING_ADDRESS)
        hex_array.append(self._LENGTH)
        hex_array += self.reserved
        hex_array.append(self.model)
        hex_array.append(self.version)
        hex_array.append(self.features)
        hex_array.append(self.end)
        return hex_array

    def from_hex_array(self, hex_array):
        self._COMMAND = hex_array[0]
        self._STARTING_ADDRESS = hex_array[1]
        self._LENGTH = hex_array[2]
        self.reserved = hex_array[3:6]
        self.model = hex_array[6]
        self.version = hex_array[7]
        self.features = hex_array[8]
        self.end = hex_array[9]

    def to_hex_string(self):
        return ''.join(['{:02X}'.format(x) for x in self.to_hex_array()])

    def to_bytes(self):
        return bytes(self.to_hex_array())

    def from_hex_string(self, hex_string):
        self.from_hex_array([int(hex_string[i:i + 2], 16) for i in range(0, len(hex_string), 2)])

    def from_bytes(self, bytes):
        self.from_hex_array([x for x in bytes])


class LoRaE22:
    # now the constructor that receive directly the UART object
    def __init__(self, model, uart, aux_pin=None, m0_pin=None, m1_pin=None,
                 gpio_mode=GPIO.BCM):
        self.uart = uart
        self.model = model

        pattern = '^(230|400|433|900|915)(T|S|M|MM)(22|27|30|33|37)(S|D|C|U|E)?..?(\\d)?$'

        model_regex = re.compile(pattern)
        if not model_regex.match(model):
            raise ValueError('Invalid model')

        self.aux_pin = aux_pin
        self.m0_pin = m0_pin
        self.m1_pin = m1_pin

        self.uart_baudrate = uart.baudrate  # This value must 9600 for configuration
        self.uart_parity = uart.parity  # This value must be the same of the module
        self.uart_stop_bits = uart.stopbits  # This value must be the same of the module

        self.gpio_mode = gpio_mode
        self.mode = None

    def begin(self):
        if not self.uart.is_open:
            self.uart.open()

        self.uart.reset_input_buffer()
        self.uart.reset_output_buffer()

        GPIO.setmode(self.gpio_mode)

        if self.aux_pin is not None:
            GPIO.setup(self.aux_pin, GPIO.IN)
        if self.m0_pin is not None and self.m1_pin is not None:
            GPIO.setup(self.m0_pin, GPIO.OUT)
            GPIO.setup(self.m1_pin, GPIO.OUT)
            GPIO.output(self.m0_pin, GPIO.HIGH)
            GPIO.output(self.m1_pin, GPIO.HIGH)

        # self.uart.timeout(1000)

        code = self.set_mode(ModeType.MODE_0_NORMAL)
        if code != ResponseStatusCode.SUCCESS:
            return code

        return code

    def set_mode(self, mode: ModeType) -> ResponseStatusCode:
        self.managed_delay(40)

        if self.m0_pin is None and self.m1_pin is None:
            logger.debug(
                "The M0 and M1 pins are not set, which means that you are connecting the pins directly as you need!")
        else:
            if mode == ModeType.MODE_0_NORMAL:
                # Mode 0 | normal operation
                GPIO.output(self.m0_pin, GPIO.LOW)
                GPIO.output(self.m1_pin, GPIO.LOW)
                logger.debug("MODE NORMAL!")
            elif mode == ModeType.MODE_1_WOR:
                # Mode 1 | wake-up operation
                GPIO.output(self.m0_pin, GPIO.HIGH)
                GPIO.output(self.m1_pin, GPIO.LOW)
                logger.debug("MODE WOR!")
            elif mode == ModeType.MODE_2_CONFIGURATION:
                # Mode 2 | power saving operation
                GPIO.output(self.m0_pin, GPIO.LOW)
                GPIO.output(self.m1_pin, GPIO.HIGH)
                logger.debug("MODE CONFIGURATION!")
            elif mode == ModeType.MODE_3_SLEEP:
                # Mode 3 | Setting operation
                GPIO.output(self.m0_pin, GPIO.HIGH)
                GPIO.output(self.m1_pin, GPIO.HIGH)
                logger.debug("MODE SLEEP!")
            else:
                return ResponseStatusCode.ERR_E22_INVALID_PARAM

        self.managed_delay(40)

        res = self.wait_complete_response(1000)
        if res == ResponseStatusCode.E22_SUCCESS:
            self.mode = mode

        return res

    @staticmethod
    def managed_delay(timeout):
        t = round(time.time()*1000)

        while round(time.time()*1000) - t < timeout:
            pass

    def wait_complete_response(self, timeout, wait_no_aux=100) -> ResponseStatusCode:
        result = ResponseStatusCode.E22_SUCCESS
        t = round(time.time()*1000)

        if self.aux_pin is not None:
            while GPIO.input(self.aux_pin) == 0:
                if round(time.time()*1000) - t > timeout:
                    result = ResponseStatusCode.ERR_E22_TIMEOUT
                    logger.debug("Timeout error!")
                    return result

            logger.debug("AUX HIGH!")
        else:
            self.managed_delay(wait_no_aux)
            logger.debug("Wait no AUX pin!")

        self.managed_delay(20)
        logger.debug("Complete!")
        return result

    def check_UART_configuration(self, mode) -> ResponseStatusCode:
        if mode == ModeType.MODE_2_PROGRAM and self.uart_baudrate != SerialUARTBaudRate.BPS_RATE_9600:
            return ResponseStatusCode.ERR_E22_WRONG_UART_CONFIG
        return ResponseStatusCode.E22_SUCCESS

    def set_configuration(self, configuration, permanent_configuration=True) -> (ResponseStatusCode, Configuration):
        # code = ResponseStatusCode.E22_SUCCESS
        code = self.check_UART_configuration(ModeType.MODE_2_PROGRAM)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        prev_mode = self.mode
        code = self.set_mode(ModeType.MODE_2_PROGRAM)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        configuration._STARTING_ADDRESS = RegisterAddress.REG_ADDRESS_CFG
        configuration._LENGTH = PacketLength.PL_CONFIGURATION

        if permanent_configuration:
            configuration._COMMAND = ProgramCommand.WRITE_CFG_PWR_DWN_SAVE
        else:
            configuration._COMMAND = ProgramCommand.WRITE_CFG_PWR_DWN_LOSE

        data = configuration.to_bytes()
        logger.debug("Writing configuration: {} size {}".format(configuration.to_hex_string(), len(data)))

        len_writed = self.uart.write(data)
        if len_writed != len(data):
            self.set_mode(prev_mode)
            return code, None

        code = self.set_mode(prev_mode)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        data = self.uart.read_all()
        logger.debug("data: {}".format(data))
        logger.debug("data len: {}".format(len(data)))

        if data is None or len(data) != PacketLength.PL_CONFIGURATION+3:
            code = ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH
            return code, None

        logger.debug("model: {}".format(self.model))
        configuration = Configuration(self.model)
        configuration.from_bytes(data)

        if ProgramCommand.WRONG_FORMAT == configuration._COMMAND:
            code = ResponseStatusCode.ERR_E22_WRONG_FORMAT
        if ProgramCommand.RETURNED_COMMAND != configuration._COMMAND or \
                RegisterAddress.REG_ADDRESS_CFG != configuration._STARTING_ADDRESS or \
                PacketLength.PL_CONFIGURATION != configuration._LENGTH:
            code = ResponseStatusCode.ERR_E22_HEAD_NOT_RECOGNIZED

        self.clean_UART_buffer()

        return code, configuration

    def write_program_command(self, cmd, addr, pl) -> int:
        cmd = bytearray([cmd, addr, pl])
        size = self.uart.write(cmd)

        self.managed_delay(50)  # need to check

        return size != 3

    def get_configuration(self) -> (ResponseStatusCode, Configuration):
        code = self.check_UART_configuration(ModeType.MODE_2_PROGRAM)
        logger.debug("check_UART_configuration: {}".format(code))
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        prev_mode = self.mode
        code = self.set_mode(ModeType.MODE_2_PROGRAM)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None
        logger.debug("set_mode: {}".format(code))

        self.write_program_command(
            ProgramCommand.READ_CONFIGURATION,
            RegisterAddress.REG_ADDRESS_CFG,
            PacketLength.PL_CONFIGURATION)

        data = self.uart.read_all()
        logger.debug("data: {}".format(data))
        logger.debug("data len: {}".format(len(data)))

        logger.debug("model: {}".format(self.model))
        configuration = Configuration(self.model)
        configuration.from_bytes(data)
        code = self.set_mode(prev_mode)

        if ProgramCommand.WRONG_FORMAT == configuration._COMMAND:
            code = ResponseStatusCode.ERR_E22_WRONG_FORMAT

        if ProgramCommand.RETURNED_COMMAND != configuration._COMMAND or \
                RegisterAddress.REG_ADDRESS_CFG != configuration._STARTING_ADDRESS or \
                PacketLength.PL_CONFIGURATION != configuration._LENGTH:
            code = ResponseStatusCode.ERR_E22_HEAD_NOT_RECOGNIZED

        return code, configuration

    def get_module_information(self):
        code = self.check_UART_configuration(ModeType.MODE_2_PROGRAM)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        prev_mode = self.mode
        code = self.set_mode(ModeType.MODE_2_PROGRAM)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        self.write_program_command(
            ProgramCommand.READ_CONFIGURATION, RegisterAddress.REG_ADDRESS_PID, PacketLength.PL_PID)

        module_information = ModuleInformation()
        data = self.uart.read(4)
        if data is None or len(data) != 4:
            code = ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH
            return code, None

        module_information.from_bytes(data)

        if code != ResponseStatusCode.E22_SUCCESS:
            self.set_mode(prev_mode)
            return code, None

        code = self.set_mode(prev_mode)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None

        if ProgramCommand.WRONG_FORMAT == module_information._COMMAND:
            code = ResponseStatusCode.ERR_E22_WRONG_FORMAT
        if ProgramCommand.RETURNED_COMMAND != module_information._COMMAND or \
                RegisterAddress.REG_ADDRESS_PID != module_information._STARTING_ADDRESS or \
                PacketLength.PL_PID != module_information._LENGTH:
            code = ResponseStatusCode.ERR_E22_HEAD_NOT_RECOGNIZED

        return code, module_information

    def reset_module(self) -> ResponseStatusCode:
        code = ResponseStatusCode.ERR_E22_NOT_IMPLEMENT
        return code

    @staticmethod
    def _normalize_array(data):
        # Convert values to valid byte values
        for i in range(len(data)):
            if data[i] > 255:
                data[i] = data[i] % 256
        return data

    def receive_dict(self, rssi=False, delimiter=None, size=None) -> (ResponseStatusCode, any, int or None):
        code, msg, rssi_value = self.receive_message(rssi, delimiter, size)
        if code != ResponseStatusCode.E22_SUCCESS:
            return code, None, None

        try:
            msg = json.loads(msg)
        except Exception as e:
            logger.error("Error: {}".format(e))
            return ResponseStatusCode.ERR_E22_JSON_PARSE, None, None

        return code, msg, rssi_value

    def receive_message(self, rssi=False, delimiter=None, size=None):
        code = ResponseStatusCode.E22_SUCCESS
        rssi_value = None
        if delimiter is not None:
            data = self._read_until(delimiter)
            if rssi:
                rssi_value = data[-1]  # last byte is rssi
                data = data[:-1]  # remove rssi from data
        elif size is not None:
            data = self.uart.read(size)
        else:
            data = self.uart.read()
            time.sleep(0.08)  # wait for the rest of the message
            while self.uart.in_waiting > 0:
                data += self.uart.read()

            self.clean_UART_buffer()
            if rssi:
                rssi_value = data[-1]  # last byte is rssi
                data = data[:-1]  # remove rssi from data

        if data is None or len(data) == 0:
            return (ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH, None, None) \
                if rssi else (ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH, None)

        data = data.decode('utf-8')
        msg = data

        return (code, msg, rssi_value) if rssi else (code, msg)

    def clean_UART_buffer(self):
        self.uart.read_all()

    def _read_until(self, terminator='\n') -> bytes:
        line = b''
        while True:
            c = self.uart.read(1)
            if c == terminator:
                break
            line += c
        return line

    def send_broadcast_message(self, CHAN, message) -> ResponseStatusCode:
        return self._send_message(message, BROADCAST_ADDRESS, BROADCAST_ADDRESS, CHAN)

    def send_broadcast_dict(self, CHAN, dict_message) -> ResponseStatusCode:
        message = json.dumps(dict_message)
        return self._send_message(message, BROADCAST_ADDRESS, BROADCAST_ADDRESS, CHAN)

    def send_transparent_message(self, message) -> ResponseStatusCode:
        return self._send_message(message)

    def send_fixed_message(self, ADDH, ADDL, CHAN, message) -> ResponseStatusCode:
        return self._send_message(message, ADDH, ADDL, CHAN)

    def send_fixed_dict(self, ADDH, ADDL, CHAN, dict_message) -> ResponseStatusCode:
        message = json.dumps(dict_message)
        return self._send_message(message, ADDH, ADDL, CHAN)

    def send_transparent_dict(self, dict_message) -> ResponseStatusCode:
        message = json.dumps(dict_message)
        return self._send_message(message)

    def _send_message(self, message, ADDH=None, ADDL=None, CHAN=None) -> ResponseStatusCode:
        result = ResponseStatusCode.E22_SUCCESS

        size_ = len(message.encode('utf-8'))
        if size_ > MAX_SIZE_TX_PACKET:
            return ResponseStatusCode.ERR_E22_PACKET_TOO_BIG

        if ADDH is not None and ADDL is not None and CHAN is not None:
            if isinstance(message, str):
                message = message.encode('utf-8')
            dataarray = bytes([ADDH, ADDL, CHAN]) + message
            dataarray = LoRaE22._normalize_array(dataarray)
            lenMS = self.uart.write(bytes(dataarray))
            size_ += 3
        elif isinstance(message, str):
            lenMS = self.uart.write(message.encode('utf-8'))
        else:
            lenMS = self.uart.write(bytes(message))

        if lenMS != size_:
            logger.debug("Send... len:", lenMS, " size:", size_)
            if lenMS == 0:
                result = ResponseStatusCode.ERR_E22_NO_RESPONSE_FROM_DEVICE
            else:
                result = ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH
        if result != ResponseStatusCode.E22_SUCCESS:
            return result

        result = self.wait_complete_response(1000)
        if result != ResponseStatusCode.E22_SUCCESS:
            return result
        logger.debug("Clear buffer...")
        self.clean_UART_buffer()

        logger.debug("ok!")
        return result

    def available(self) -> int:
        return self.uart.in_waiting

    def end(self) -> ResponseStatusCode:
        try:
            if self.uart is not None:
                self.uart.close()
                del self.uart
                GPIO.cleanup()
            return ResponseStatusCode.E22_SUCCESS

        except Exception as E:
            logger.error("Error: {}".format(E))
            return ResponseStatusCode.ERR_E22_DEINIT_UART_FAILED
