#!/usr/bin/env python

import sys
sys.path.append('..')

from sportiduino import Sportiduino
import serial


#ser = serial.Serial('/dev/pts/12')
#ser.write(b'\xfe')
sportiduino = Sportiduino(port='/dev/pts/12', debug=True)
#sportiduino = Sportiduino(debug=True)

print('beep_ok')
sportiduino.beep_ok()
print('beep_error')
sportiduino.beep_error()
