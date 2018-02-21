#!/usr/bin/env python

import os, pty


class FakeMasterStation(object):
    
    def __init__(self):
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        print("FakeMasterStation port: %s" % s_name)
        self.master = master
        self.slave = slave
        self.port = s_name

    def read(self):
        cmd = os.read(self.master,4)
        if cmd == b'\xfe\x46\x00\x46':
            os.write(self.master, b'\xfe\x66\x01\x66\xcd')
        

if __name__ == "__main__":
    fms = FakeMasterStation()
    print('Reading...')
    while True:
        fms.read()

