#!/usr/bin/env python

import os, pty

from six import int2byte, byte2int, iterbytes, PY3
from time import sleep

if PY3:
    def byte2int(x):
        try:
            return x[0]
        except TypeError:
            return x


class FakeMasterStation(object):
    
    def __init__(self):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        print("FakeMasterStation port: %s" % s_name)
        self.master = master
        self.slave = slave
        self.port = s_name

    def read(self):
        cmd = os.read(self.master,32)
        print("=> %s" % ' '.join(hex(byte2int(c)) for c in cmd))
        if cmd == b'\xfe\x46\x00\x46':
            os.write(self.master, b'\xfe\x66\x01\xd2\x39') # version 2.10
        elif cmd == b'\xfe\x59\x00\x59':
            os.write(self.master, b'\xfe\x79\x00\x79') # send Ok
        elif cmd == b'\xfe\x58\x00\x58':
            os.write(self.master, b'\xfe\x79\x00\x79') # send Ok
            #os.write(self.master, b'\xfe\x78\x01\x01\x7a') # send COM err
        elif cmd[:3] == b'\xfe\x41\x06':
            os.write(self.master, b'\xfe\x79\x00\x79') # send Ok
        elif cmd[:3] == b'\xfe\x42\x01':
            os.write(self.master, b'\xfe\x79\x00\x79') # send Ok
        elif cmd[:3] == b'\xfe\x44\x0e':
            os.write(self.master, b'\xfe\x79\x00\x79') # send Ok
        elif cmd == b'\xfe\x4b\x00\x4b':
            os.write(self.master, b'\xfe\x63\x1e'
                                + b'\x00\x09'
                                + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                                + b'\xf0'
                                + b'\x5a\x9d\x3c\xab'
                                + b'\x1f'
                                + b'\x5a\x9d\x3d\x0f'
                                + b'\x20'
                                + b'\x5a\x9d\x3d\x55'
                                + b'\x21'
                                + b'\x5a\x9d'
                                + b'\x7b')
            os.write(self.master, b'\xfe\x63\x07'
                                + b'\x3d\xc3'
                                + b'\xf5'
                                + b'\x5a\x9d\x3e\x5b'
                                + b'\xef')


if __name__ == "__main__":
    fms = FakeMasterStation()
    print('Reading...')
    while True:
        fms.read()

