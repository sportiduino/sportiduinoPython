#!/usr/bin/env python

import sys
sys.path.append('..')

from sportiduino import Sportiduino
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

print('set_time')
sportiduino.set_time()

print('set_cp_number')
sportiduino.set_cp_number(31)

print('init_card')
sportiduino.init_card(2)

