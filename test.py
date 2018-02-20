#!/usr/bin/env python

from sportiduino import Sportiduino
import os, pty
import serial


#master, slave = pty.openpty()
#s_name = os.ttyname(slave)
#print(s_name)
#sportiduino = Sportiduino(port=s_name, debug=True)

sportiduino = Sportiduino(debug=True)

print('beep_ok')
sportiduino.beep_ok()
print('beep_error')
sportiduino.beep_error()

