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


print('Read card loop')
while True:
    while not sportiduino.poll_card():
        sleep(1)

    data = sportiduino.card_data
    print("Punches:", data)
    sportiduino.beep_ok()

