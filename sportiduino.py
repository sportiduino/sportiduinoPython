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
from datetime import datetime
import time
#from binascii import hexlify
import os
import platform
import re

if PY3:
    def byte2int(x):
        try:
            return x[0]
        except TypeError:
            return x

class Sportiduino(object):

    # Constants
    START_BYTE = b'\xfe'

    OFFSET = 0x1E

    MAX_DATA_LEN = 25

    START_STATION = 240
    FINISH_STATION = 245

    CMD_WRITE_TIME      = b'\x41'
    CMD_WRITE_CP_NUM    = b'\x42'
    CMD_WRITE_PASSWD    = b'\x43'
    CMD_INIT_CARD       = b'\x44'
    CMD_WRITE_PAGES6_7  = b'\x45'
    CMD_READ_VERS       = b'\x46'
    CMD_INIT_LOGREADER  = b'\x47'
    CMD_READ_LOGREADER  = b'\x48'
    CMD_SET_READ_MODE   = b'\x49'
    CMD_READ_CARD       = b'\x4b'
    CMD_READ_RAW        = b'\x4c'
    CMD_INIT_SLEEPCARD  = b'\x4e'
    CMD_BEEP_ERROR      = b'\x58'
    CMD_BEEP_OK         = b'\x59'

    RESP_LOG            = b'\x61'
    RESP_CARD_DATA      = b'\x63'
    RESP_CARD_RAW       = b'\x65'
    RESP_VERS           = b'\x66'
    RESP_MODE           = b'\x69'
    RESP_ERROR          = b'\x78'
    RESP_OK             = b'\x79'

    ERR_COM             = b'\x01'
    ERR_WRITE_CARD      = b'\x02'
    ERR_READ_CARD       = b'\x03'

    class Version(object):
        def __init__(self, value):
            self.value = value
            self.major = value // 100
            self.minor = value % 100

        def __str__(self):
            return 'v%d.%d.x' % (self.major, self.minor)

    def __init__(self, port=None, debug=False):
        self._serial = None
        self._debug = debug

        errors = ''
        if port is not None:
            self._connect_master_station(port)
            return
        else:
            if platform.system() == 'Linux':
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
            elif platform.system() == 'Windows':
                for i in range(32):
                    try:
                        port = 'COM' + str(i)
                        self._connect_master_station(port)
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


    def read_version(self):
        code, data = self._send_command(Sportiduino.CMD_READ_VERS)
        if code == Sportiduino.RESP_VERS:
            return Sportiduino.Version(byte2int(data))
        return None


    def read_card(self, blocking=True):
        code, data = self._send_command(Sportiduino.CMD_READ_CARD, blocking=blocking)
        if code == Sportiduino.RESP_CARD_DATA:
            return self._parse_card_data(data)
        else:
            raise SportiduinoException("Read card failed.")


    def read_card_raw(self, blocking=True):
        code, data = self._send_command(Sportiduino.CMD_READ_RAW, blocking=blocking)
        if code == Sportiduino.RESP_CARD_RAW:
            return self._parse_card_raw_data(data)
        else:
            raise SportiduinoException("Read raw data failed.")


    def read_log(self, blocking=True):
        code, data = self._send_command(Sportiduino.CMD_READ_LOGREADER, blocking=blocking)
        if code == Sportiduino.RESP_LOG:
            return self._parse_log(data)
        else:
            raise SportiduinoException("Read log failed.")


    def init_card(self, card_number, page6=None, page7=None):
        #TODO: check page6 and page7 length
        if page6 is None:
            page6 = b'\x00\x00\x00\x00'
        if page7 is None:
            page7 = b'\x00\x00\x00\x00'

        params = bytearray()
        params += Sportiduino._to_str(card_number, 2)
        t = int(time.time())
        params += Sportiduino._to_str(t, 4)
        params += page6[:5]
        params += page7[:5]
        self._send_command(Sportiduino.CMD_INIT_CARD, params)


    def init_logreader(self):
        self._send_command(Sportiduino.CMD_INIT_LOGREADER)


    def init_sleepcard(self):
        self._send_command(Sportiduino.CMD_INIT_SLEEPCARD)


    def write_cp_number(self, cp_number):
        params = int2byte(cp_number)
        self._send_command(Sportiduino.CMD_WRITE_CP_NUM, params)


    def write_time(self, time=datetime.today()):
        params = bytearray()
        params.append(time.year - 2000)
        params.append(time.month)
        params.append(time.day)
        params.append(time.hour)
        params.append(time.minute)
        params.append(time.second)
        self._send_command(Sportiduino.CMD_WRITE_TIME, params)


    def write_passwd(self, old_passwd, new_passwd, settings):
        params = bytearray()
        params += Sportiduino._to_str(new_passwd, 3)
        params += Sportiduino._to_str(old_passwd, 3)
        params += Sportiduino._to_str(settings, 1)
        self._send_command(Sportiduino.CMD_WRITE_PASSWD, params)


    def write_pages6_7(self, page6, page7):
        params = bytearray()
        params += page6[:5]
        params += page7[:5]
        self._send_command(Sportiduino.CMD_WRITE_PAGES6_7, params)


    def enable_continuous_read(self):
        self._set_mode(b'\x01')


    def disable_continuous_read(self):
        self._set_mode(b'\x00')


    def _set_mode(self, mode):
        self._send_command(Sportiduino.CMD_SET_READ_MODE, mode)


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
        version = self.read_version()
        if version is not None:
            print("Master station %s on port '%s' connected" % (version, port))


    def _send_command(self, code, parameters=None, blocking=False):
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
        self._serial.write(cmd)

        while True:
            try:
                resp_code, data = self._read_response()
                break
            except SportiduinoTimeout as msg:
                if not blocking:
                    raise SportiduinoTimeout(msg)

        return Sportiduino._preprocess_response(resp_code, data, self._debug)


    def _read_response(self, timeout=None, wait_fragment=None):
        try:
            if timeout is not None:
                old_timeout = self._serial.timeout
                self._serial.timeout = timeout
            byte = self._serial.read()
            if timeout is not None:
                self._serial.timeout = old_timeout 
            if byte == b'':
                raise SportiduinoTimeout('No response')
            elif byte != Sportiduino.START_BYTE:
                self._serial.reset_input_buffer()
                raise SportiduinoException('Invalid start byte 0x%s' % hex(byte2int(byte)))

            code = self._serial.read()
            length_byte = self._serial.read()
            length = byte2int(length_byte)

            more_fragments = False
            if length > Sportiduino.OFFSET:
                more_fragments = True
                fragment_num = length - Sportiduino.OFFSET
                if fragment_num != 1 and wait_fragment is not None:
                    if fragment_num != wait_fragment:
                        raise SportiduinoException('Waiting fragment %d, receive %d' % (wait_fragment, fragment_num))
                length = Sportiduino.MAX_DATA_LEN
            data = self._serial.read(length)
            checksum = self._serial.read()
            if self._debug:
                print("<= code '%s', len %i, data %s, cs %s" % (hex(byte2int(code)),
                                                                length,
                                                                ' '.join(hex(byte2int(c)) for c in data),
                                                                hex(byte2int(checksum))
                                                                ))

            if not Sportiduino._cs_check(code + length_byte + data, checksum):
                raise SportiduinoException('Checksum mismatch')

        except (SerialException, OSError) as msg:
            raise SportiduinoException('Error reading response: %s' % msg)

        if more_fragments:
            next_code, next_data = self._read_response(timeout, fragment_num + 1)
            if next_code == code:
                data += next_data

        return code, data


    def __del__(self):
        if self._serial is not None:
            self._serial.close()


    @staticmethod
    def _to_int(s):
        """Compute the integer value of a raw byte string (big endianes)."""
        value = 0
        for offset, c in enumerate(iterbytes(s[::-1])):
            value += c << offset*8
        return value


    @staticmethod
    def _to_str(i, len):
        if PY3:
            return i.to_bytes(len, 'big')
        if i >> len*8 != 0:
            raise OverflowError('%i too big to convert to %i bytes' % (i, len))
        string = ''
        for offset in range(len-1, -1, -1):
            string += int2byte((i >> offset*8) & 0xff)
        return string


    @staticmethod
    def _preprocess_response(code, data, debug=False):
        if code == Sportiduino.RESP_ERROR:
            if data == Sportiduino.ERR_COM:
                raise SportiduinoException("COM error")
            elif data == Sportiduino.ERR_WRITE_CARD:
                raise SportiduinoException("Card write error")
            elif data == Sportiduino.ERR_READ_CARD:
                raise SportiduinoException("Card read error")
        elif code == Sportiduino.RESP_OK and debug:
            print("Ok received")
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

 
    @staticmethod
    def _parse_card_data(data):
        # TODO check data length
        ret = {}
        ret['card_number'] = Sportiduino._to_int(data[0:2])
        ret['page6'] = data[2:6]
        ret['page7'] = data[6:10]
        ret['punches'] = []
        for i in range(10, len(data), 5):
            cp = byte2int(data[i])
            time = datetime.fromtimestamp(Sportiduino._to_int(data[i + 1:i + 5]))
            if cp == Sportiduino.START_STATION:
                ret['start'] = time
            elif cp == Sportiduino.FINISH_STATION:
                ret['finish'] = time
            else:
                ret['punches'].append((cp, time))

        return ret


    @staticmethod
    def _parse_card_raw_data(data):
        ret = {}
        for i in range(0, len(data), 5):
            page_num = byte2int(data[i])
            ret[page_num] = data[i + 1:i + 4]

        return ret


    @staticmethod
    def _parse_log(data):
        ret = {}
        cp = byte2int(data[0])
        ret['cp'] = cp
        ret['cards'] = []
        for i in range(1, len(data), 2):
            ret['cards'].append(Sportiduino._to_int(data[i:i + 1]))

        return ret



class SportiduinoException(Exception):
    pass


class SportiduinoTimeout(SportiduinoException):
    pass

