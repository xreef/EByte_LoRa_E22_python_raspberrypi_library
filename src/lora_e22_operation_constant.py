class ModeType:
    MODE_0_NORMAL = 0
    MODE_1_WOR = 1
    MODE_2_CONFIGURATION = 2
    MODE_2_PROGRAM = 2
    MODE_3_SLEEP = 3
    MODE_INIT = 0xFF


class ProgramCommand:
    WRITE_CFG_PWR_DWN_SAVE = 0xC0
    READ_CONFIGURATION = 0xC1
    WRITE_CFG_PWR_DWN_LOSE = 0xC2
    WRONG_FORMAT = 0xFF
    RETURNED_COMMAND = 0xC1
    SPECIAL_WIFI_CONF_COMMAND = 0xCF


class RegisterAddress:
    REG_ADDRESS_CFG = 0x00
    REG_ADDRESS_SPED = 0x03
    REG_ADDRESS_TRANS_MODE = 0x04
    REG_ADDRESS_CHANNEL = 0x05
    REG_ADDRESS_OPTION = 0x06
    REG_ADDRESS_CRYPT = 0x07
    REG_ADDRESS_PID = 0x80


class PacketLength:
    PL_CONFIGURATION = 0x09
    PL_SPED = 0x01
    PL_OPTION = 0x01
    PL_TRANSMISSION_MODE = 0x01
    PL_CHANNEL = 0x01
    PL_CRYPT = 0x02
    PL_PID = 7


class ResponseStatusCode:
    SUCCESS = 1
    E22_SUCCESS = 1
    ERR_E22_UNKNOWN = 2
    ERR_E22_NOT_SUPPORT = 3
    ERR_E22_NOT_IMPLEMENT = 4
    ERR_E22_NOT_INITIAL = 5
    ERR_E22_INVALID_PARAM = 6
    ERR_E22_DATA_SIZE_NOT_MATCH = 7
    ERR_E22_BUF_TOO_SMALL = 8
    ERR_E22_TIMEOUT = 9
    ERR_E22_HARDWARE = 10
    ERR_E22_HEAD_NOT_RECOGNIZED = 11
    ERR_E22_NO_RESPONSE_FROM_DEVICE = 12
    ERR_E22_WRONG_UART_CONFIG = 13
    ERR_E22_PACKET_TOO_BIG = 14
    ERR_E22_JSON_PARSE = 15
    ERR_E22_DEINIT_UART_FAILED = 16
    ERR_E22_WRONG_FORMAT = 17

    @staticmethod
    def get_description(status):
        if status == ResponseStatusCode.E22_SUCCESS:
            return "Success"
        elif status == ResponseStatusCode.ERR_E22_UNKNOWN:
            return "Unknown"
        elif status == ResponseStatusCode.ERR_E22_NOT_SUPPORT:
            return "Not support!"
        elif status == ResponseStatusCode.ERR_E22_NOT_IMPLEMENT:
            return "Not implement"
        elif status == ResponseStatusCode.ERR_E22_NOT_INITIAL:
            return "Not initial!"
        elif status == ResponseStatusCode.ERR_E22_INVALID_PARAM:
            return "Invalid param!"
        elif status == ResponseStatusCode.ERR_E22_DATA_SIZE_NOT_MATCH:
            return "Data size not match!"
        elif status == ResponseStatusCode.ERR_E22_BUF_TOO_SMALL:
            return "Buff too small!"
        elif status == ResponseStatusCode.ERR_E22_TIMEOUT:
            return "Timeout!!"
        elif status == ResponseStatusCode.ERR_E22_HARDWARE:
            return "Hardware error!"
        elif status == ResponseStatusCode.ERR_E22_HEAD_NOT_RECOGNIZED:
            return "Save mode returned not recognized!"
        elif status == ResponseStatusCode.ERR_E22_NO_RESPONSE_FROM_DEVICE:
            return "No response from device! (Check wiring)"
        elif status == ResponseStatusCode.ERR_E22_WRONG_UART_CONFIG:
            return "Wrong UART configuration! (BPS must be 9600 for configuration)"
        elif status == ResponseStatusCode.ERR_E22_PACKET_TOO_BIG:
            return "The device support only 58byte of data transmission!"
        elif status == ResponseStatusCode.ERR_E22_JSON_PARSE:
            return "JSON parse error!"
        elif status == ResponseStatusCode.ERR_E22_DEINIT_UART_FAILED:
            return "Deinit UART failed!"
        elif status == ResponseStatusCode.ERR_E22_WRONG_FORMAT:
            return "Wrong format!"
        else:
            return "Invalid status!"


class SerialUARTBaudRate:
    BPS_RATE_1200 = 1200
    BPS_RATE_2400 = 2400
    BPS_RATE_4800 = 4800
    BPS_RATE_9600 = 9600
    BPS_RATE_19200 = 19200
    BPS_RATE_38400 = 38400
    BPS_RATE_57600 = 57600
    BPS_RATE_115200 = 115200

