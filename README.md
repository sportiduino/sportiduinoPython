# Sportiduino Reader

This is Python module to communicate with the Sportiduino master station.


## Usage

To use the Sportiduino master station for card readout:

    from sportiduino import Sportiduino
    from time import sleep

    # Connect to master station, the station is automatically detected.
    # If this does not work, give the path to the port as an argument.
    sportiduino = Sportiduino()

    # Wait for a card to be inserted into the master station
    while not sportiduino.poll_card():
        sleep(0.5)

    # Now card data is set
    data = sportiduino.card_data

    sportiduino.beep_ok()

    print("Card data:", data)
    # Card data: {
    #   'card_number': 9,
    #   'start': datetime.datetime(2018, 3, 5, 15, 48, 43),
    #   'finish': datetime.datetime(2018, 3, 5, 15, 55, 55),
    #   'punches': [
    #     (31, datetime.datetime(2018, 3, 5, 15, 50, 23)),
    #     (32, datetime.datetime(2018, 3, 5, 15, 51, 33)),
    #     (33, datetime.datetime(2018, 3, 5, 15, 53, 23))
    #   ],
    #   'page6': b'\x00\x00\x00\x00',
    #   'page7': b'\x00\x00\x00\x00'
    # }


## Testing

Connect master station and run test script from `test` directory

    python test.py

You can run test with port name. For Linux
    
    python test.py /dev/ttyUSB0

or for Windows
    
    python test.py COM3

