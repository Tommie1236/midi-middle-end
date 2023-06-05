from prettyprinter import pprint
from termcolor import colored
import pygame
import pygame.midi
import time


devices_info = {
		'x-touch-in':   [None, None],
		'x-touch-out':  [None, None],
		'loopmidi-in':  [None, None],
		'loopmidi-out': [None, None]
		}

SEGMENT_DATA = {
	0: 0b01111111,
	1: 0b0000110,
	2: 0b1011011,
	3: 0b1001111,
	4: 0b1100110,
	5: 0b1101101,
	6: 0b1111101,
	7: 0b0000111,
	8: 0b1111111,
	9: 0b1101111,
	'a': 0b1110111,
	'b': 0b1111100, 
	'c': 0b0111001,
	'd': 0b1011110
}

def midi_connect() -> None:

	dev_count = pygame.midi.get_count()
	if dev_count == 0:
		print("No MIDI devices found.")
		return

	print("Available MIDI devices:")
	for i in range(dev_count):
		device_info = pygame.midi.get_device_info(i)
		device_name = device_info[1].decode("utf-8")
		print(f"[{i}] - {device_name}")
	
	
	for port, io in [('x-touch-in', 'in'), ('x-touch-out', 'out')]: #, ('loopmidi-in', 'in'), ('loopmidi-out', 'out')]:
		while True:
			try:
				dev_idx = int(input(f'Enter index of <{port}>: '))
				if 0 <= dev_idx < dev_count:
					break
				else:
					print('Invalid device index. Please try again.')
			except ValueError:
				print('Invalid input. Please enter a valid device index.')

		if io == 'in': 		devices_info[port][0] = pygame.midi.Input(dev_idx)
		elif io == 'out':	devices_info[port][0] = pygame.midi.Output(dev_idx)
		else:				print(f'i/o method <{io}> not valid.')
		
		devices_info[port][1] = dev_idx

def print_data_in():
	while True:
		...

if __name__ == '__main__':
	try:
		pygame.init()
		pygame.midi.init()
		# text = [SEGMENT_DATA['a'], SEGMENT_DATA['b'], SEGMENT_DATA['c'], SEGMENT_DATA['d'], SEGMENT_DATA[0]]
		# sysex_data = [0xF0, 0x00, 0x20, 0x32, 0x14, 0x37]
		# sysex_data.extend(text)
		# sysex_data.extend([0x00, 0x00, 0xF7])
		sysex_message_segment_displays = [0xF0, 0x00, 0x20, 0x32, 0x14, 0x37]
		sysex_message_segment_displays.extend([SEGMENT_DATA['a'], SEGMENT_DATA['b'], SEGMENT_DATA['c'], SEGMENT_DATA['d'], SEGMENT_DATA[0]])
		sysex_message_segment_displays.extend([0x00, 0x00])
		sysex_message_segment_displays.extend([0xF7])
		midi_connect()
		print('\ndevices_info:')
		pprint(devices_info)
		midi_out = devices_info['x-touch-out'][0]
		midi_out.write_sys_ex(pygame.midi.time(), sysex_message_segment_displays)
		time.sleep(0.1)
		print_data_in()

	except KeyboardInterrupt:
		pass
	finally:
		
		if devices_info['x-touch-in'][0]: devices_info['x-touch-in'][0].close()
		if devices_info['x-touch-out'][0]: devices_info['x-touch-out'][0].close()
		if devices_info['loopmidi-in'][0]: devices_info['loopmidi-in'][0].close()
		if devices_info['loopmidi-out'][0]: devices_info['loopmidi-out'][0].close()

		pygame.midi.quit()
		pygame.quit()