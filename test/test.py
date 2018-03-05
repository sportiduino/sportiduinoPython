#!/usr/bin/env python

import sys
sys.path.append('..')

from sportiduino import Sportiduino
from time import sleep
import serial

if len(sys.argv) > 1:
    port = sys.argv[1]
    sportiduino = Sportiduino(port=port, debug=True)
else:
    sportiduino = Sportiduino(debug=True)


print('beep_ok')
sportiduino.beep_ok()

print('beep_error')
sportiduino.beep_error()

print('Read card loop')
while True:
    # Read card or wait
    data = sportiduino.read_card()
    sportiduino.beep_ok()
    print("Punches:", data)


