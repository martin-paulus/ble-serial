from virtual_serial import UART
from interface import BLE_interface
from bluepy.btle import BTLEDisconnectError
import logging, sys, argparse

parser = argparse.ArgumentParser(description='Create virtual serial ports from BLE devices.')
parser.add_argument('-v', dest='verbose', action='store_true',
    help='Increase verbosity (logs all data going through)')
parser.add_argument('-d', '--dev', dest='device', required=True,
    help='BLE device address to connect (hex)')
parser.add_argument('-w', '--write-uuid', dest='write_uuid', required=False,
    help='The GATT chracteristic to write the serial data, you might use "scan.py -v" to find it out')
args = parser.parse_args()
print(args)

logging.basicConfig(
    format='%(asctime)s.%(msecs)d | %(levelname)s | %(filename)s: %(message)s', 
    datefmt='%H:%M:%S',
    level=logging.DEBUG if args.verbose else logging.INFO
)

# addr_str = '20:91:48:4c:4c:54'
# addr_str = 'a4:c1:38:3a:08:b1'
write_uid = '0000ffe1-0000-1000-8000-00805f9b34fb'
# write_uid = '0000ff02-0000-1000-8000-00805f9b34fb'

if __name__ == '__main__':
    try:
        uart = UART()
        bt = BLE_interface(args.device, write_uid)
        bt.set_receiver(uart.write_sync)
        uart.set_receiver(bt.send)

        logging.info('Running main loop!')
        uart.start()
        while True:
            bt.receive_loop()
    except (BTLEDisconnectError, KeyboardInterrupt):
        logging.warning('Shutdown initiated')
        uart.stop()
        bt.shutdown()
        logging.info('Shutdown complete.')
        exit(0)
    except Exception as e:
        logging.error(f'Unexpected Error: {e}')