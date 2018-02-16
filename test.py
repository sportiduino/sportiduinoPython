#!/usr/bin/env python

from sportiduino import Sportiduino


sportiduino = Sportiduino('/dev/ttyUSB0', True)

print('beep_ok')
sportiduino.beep_ok()
print('beep_error')
sportiduino.beep_error()

