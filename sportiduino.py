#/usr/bin/env python

class Sportiduino(object):

    # Constants
    STX_BYTE = 0xFE

    OFFSET = 0x1E

    MAX_DATA_LEN = 25

    CMD_SET_TIME        = 0x41
    CMD_SET_ID          = 0x42
    CMD_SET_PASSWD      = 0x43
    CMD_INIT_CARD       = 0x44
    CMD_SET_PAGES67     = 0x45
    CMD_SET_LOGREADER   = 0x47 # ?
    CMD_GET_LOGREADER   = 0x48 # ?
    CMD_READ_CARD       = 0x4B
    CMD_READ_RAW        = 0x4C
    CMD_WRITE_SLEEPCARD = 0x4E
    CMD_ERROR_BEEP      = 0x58
    CMD_OK_BEEP         = 0x59

    RESP_LOG            = 0x61
    RESP_CARD_DATA      = 0x63
    RESP_CARD_RAW       = 0x65
    RESP_ERROR          = 0x78
    RESP_OK             = 0x79

    ERR_COM             = 0x01
    ERR_WRITE_CARD      = 0x02
    ERR_READ_CARD       = 0x03


