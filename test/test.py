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

#print('read_card')
#data = sportiduino.read_card()
#print("Punches:", data)
#print('beep_ok')
#sportiduino.beep_ok()

print('Read card loop')
while True:
    while not sportiduino.poll_card():
        sleep(1)

    data = sportiduino.card_data
    print("Punches:", data)
    sportiduino.beep_ok()

