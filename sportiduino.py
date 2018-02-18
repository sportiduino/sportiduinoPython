#!/usr/bin/env python
#
#    Copyright 2018 Semyon Yakimov <ya-kimov@mail.ru>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
sportiduino.py - Classes to work with Sportiduino v1.2.0 and above.
"""

from six import int2byte, byte2int, iterbytes, PY3
from serial import Serial
from serial.serialutil import SerialException
#from binascii import hexlify
import os, re

class Sportiduino(object):

    # Constants
    START_BYTE = b'\xfe'

    OFFSET = 0x1E

    MAX_DATA_LEN = 25

    CMD_SET_TIME        = b'\x41'
    CMD_SET_ID          = b'\x42'
    CMD_SET_PASSWD      = b'\x43'
    CMD_INIT_CARD       = b'\x44'
    CMD_SET_PAGES6_7    = b'\x45'
    CMD_READ_VERS       = b'\x46'
    CMD_WRITE_LOGREADER = b'\x47'
    CMD_READ_LOGREADER  = b'\x48'
    CMD_READ_CARD       = b'\x4b'
    CMD_READ_RAW        = b'\x4c'
    CMD_WRITE_SLEEPCARD = b'\x4e'
    CMD_BEEP_ERROR      = b'\x58'
    CMD_BEEP_OK         = b'\x59'

    RESP_LOG            = b'\x61'
    RESP_CARD_DATA      = b'\x63'
    RESP_CARD_RAW       = b'\x65'
    RESP_VERS           = b'\x66'
    RESP_ERROR          = b'\x78'
    RESP_OK             = b'\x79'

    ERR_COM             = b'\x01'
    ERR_WRITE_CARD      = b'\x02'
    ERR_READ_CARD       = b'\x03'


    def __init__(self, port=None, debug=False):
        self._serial = None
        self._debug = debug

        errors = ''
        if port is not None:
            self._connect_master_station(port)
            return
        else:
            # Linux
            scan_ports = [ os.path.join('/dev', f) for f in os.listdir('/dev') if
                           re.match('ttyUSB.*', f) ]

            if len(scan_ports) == 0:
                errors = 'no serial ports found'

            for port in scan_ports:
                try:
                    self._connect_master_station(port)
                    return
                except SportiduinoException as msg:
                    errors += 'port %s: %s\n' % (port, msg)

        raise SportiduinoException('No Sportiduino master station found. Possible reasons: %s' % errors)

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
        cmd = Sportiduino.START_BYTE + cmd_string + cs

        if self._debug:
            print("=> %s" % ' '.join(hex(byte2int(c)) for c in cmd))
            #print("=> command '%s', parameters %s, cs %s" % (hexlify(code).decode('ascii'),
            #                                                 ' '.join([hexlify(int2byte(c)).decode('ascii') for c in parameters]),
            #                                                 hexlify(cs).decode('ascii'),
            #                                                 ))
        #self._serial.write(cmd)

        return Sportiduino._preprocess_response(self._read_response())


    def _read_response(self, timeout=None):
        try:
            if timeout is not None:
                old_timeout = self._serial.timeout
                self._serial.timeout = timeout
            byte = self._serial.read()
            if timeout is not None:
                self._serial.timeout = old_timeout

            if byte == b'':
                raise SportiduinoException('No response')
            elif byte != START_BYTE:
                self._serial.reset_input_buffer()
                raise SportiduinoException('Invalid start byte 0x%s' % hex(byte2int(byte)))

            code = self._serial.read()
            length_byte = self._serial.read()
            length = byte2int(length_byte)

            need_read_next_packet = False
            if length > Sportiduino.OFFSET:
                # TODO check complete set of packets
                need_read_next_packet = True
                length = MAX_DATA_LEN
            data = self._serial.read(length)
            checksum = self._serial.read()
            if self._debug:
                print("<= code '%s', len %i, data %s, cs %s" % (hex(byte2int(code)),
                                                                length,
                                                                ' '.join(hex(byte2int(c)) for c in data),
                                                                hex(byte2int(checksum))
                                                                ))

            if not Sportiduino._cs_check(cmd + length_byte + data, checksum):
                raise SportiduinoException('Checksum mismatch')

        except (SerialException, OSError) as msg:
            raise SportiduinoException('Error reading response: %s' % msg)

        if need_read_next_packet:
            data += self._read_response(timeout)

        return code, data


    def __del__(self):
        if self._serial is not None:
            self._serial.close()

    @staticmethod
    def _to_int(s)
        """Compute the integer value of a raw byte string (big endianes)."""
        value = 0
        for offset, c in enumerate(iterbytes(s[::-1])):
            value += c << offset*8
        return value


    @staticmethod
    def _preprocess_response(code, data):
        if code == RESP_ERROR:
            if data == ERR_COM:
                raise SportiduinoException("COM error")
            elif data == ERR_WRITE_CARD:
                raise SportiduinoException("Card write error")
            elif data == ERR_READ_CARD:
                raise SportiduinoException("Card read error")
        return code, data


    @staticmethod
    def _checsum(s):
        sum = 0
        for c in s:
            sum += byte2int(c)
        sum &= 0xff
        return int2byte(sum)


    @staticmethod
    def _cs_check(s, checksum):
        return Sportiduino._checsum(s) == checksum



class SportiduinoReadout(Sportiduino):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)


    def read_card(self):
        code, data = self._send_command(Sportiduino.CMD_READ_CARD)
        if code == RESP_CARD_DATA:
            self._parse_card_data(data)


    def read_card_raw(self):
        code, data = self._send_command(Sportiduino.CMD_READ_RAW)
        if code == RESP_CARD_RAW:
            self._parse_card_raw_data(data)


    def read_log(self):
        code, data = self._send_command(Sportiduino.CMD_READ_LOGREADER)
        if code == RESP_LOG:
            self._parse_log(data)


    def _parse_card_data(self, data):
        # TODO check data length
        ret = {}
        ret['card_number'] = Sportiduino._to_int(data[0:1])
        ret['page6'] = data[2:5]
        ret['page7'] = data[6:9]
        # TODO read punches

        return ret


    def _parse_card_raw_data(self, data):
        # TODO
        pass


    def _parse_log(data):
        # TODO
        pass



class SportiduinoException(Exception):
    pass

