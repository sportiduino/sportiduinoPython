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

print('init_card')
sportiduino.init_card(card_number=2)

print('read_card')
data = sportiduino.read_card()
print(data)


