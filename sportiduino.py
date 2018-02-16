#!/usr/bin/env python

from six import int2byte, byte2int
from serial import Serial
from serial.serialutil import SerialException
#from binascii import hexlify
import os

class Sportiduino(object):

    # Constants
    START_SEQ = b'\xfe\xfe\xfe\xfe'

    OFFSET = 0x1E

    MAX_DATA_LEN = 25

    CMD_SET_TIME        = b'\x41'
    CMD_SET_ID          = b'\x42'
    CMD_SET_PASSWD      = b'\x43'
    CMD_INIT_CARD       = b'\x44'
    CMD_SET_PAGES67     = b'\x45'
    CMD_SET_LOGREADER   = b'\x47' # ?
    CMD_GET_LOGREADER   = b'\x48' # ?
    CMD_READ_CARD       = b'\x4b'
    CMD_READ_RAW        = b'\x4c'
    CMD_WRITE_SLEEPCARD = b'\x4e'
    CMD_BEEP_ERROR      = b'\x58'
    CMD_BEEP_OK         = b'\x59'

    RESP_LOG            = b'\x61'
    RESP_CARD_DATA      = b'\x63'
    RESP_CARD_RAW       = b'\x65'
    RESP_ERROR          = b'\x78'
    RESP_OK             = b'\x79'

    ERR_COM             = 0x01
    ERR_WRITE_CARD      = 0x02
    ERR_READ_CARD       = 0x03


    def __init__(self, port=None, debug=False):
        self._serial = None
        self._debug = debug


    def beep_ok(self):
        self._send_command(Sportiduino.CMD_BEEP_OK)


    def beep_error(self):
        self._send_command(Sportiduino.CMD_BEEP_ERROR)


    def disconnect(self):
        self._serial.close()


    def reconnect(self):
        self.disconnect()
        self._connect_master_station(self._serial.port)


    def _connect_master_station(self, port):
        try:
            self._serial = Serial(port, baudrate=9600, timeout=5)
        except (SerialException, OSError):
            raise SportiduinoException("Could not open port '%s'" % port)

        try:
            self._serial.reset_input_buffer()
        except (SerialException, OSError):
            raise SportiduinoException("Could not flush port '%s'" % port)

        self.port = port
        self.baudrate = self._serial.baudrate


    def _send_command(self, code, parameters=None):
        if parameters is None:
            parameters = b''
        data_len = len(parameters)
        if data_len > Sportiduino.MAX_DATA_LEN:
            raise SportiduinoException("Command too long: %d" % data_len)
        cmd_string = code + int2byte(data_len) + parameters

        cs = self._checsum(cmd_string)
        cmd = Sportiduino.START_SEQ + cmd_string + cs

        if self._debug:
            print("=> %s" % ' '.join(hex(byte2int(c)) for c in cmd))
            #print("=> command '%s', parameters %s, cs %s" % (hexlify(code).decode('ascii'),
            #                                                 ' '.join([hexlify(int2byte(c)).decode('ascii') for c in parameters]),
            #                                                 hexlify(cs).decode('ascii'),
            #                                                 ))
        #self._serial.write(cmd)

        return self._read_response()


    def _read_response(self):
        # TODO
        return


    @staticmethod
    def _checsum(s):
        sum = 0
        for c in s:
            sum += byte2int(c)
        sum &= 0xff
        return int2byte(sum)


class SportiduinoException(Exception):
    pass
