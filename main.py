from prettyprinter import pprint
from termcolor import colored
import pygame
import pygame.midi



devices_info = {
		'x-touch-in':   (None, None),
		'x-touch-out':  (None, None),
		'loopmidi-in':  (None, None),
		'loopmidi-out': (None, None)
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
	
	
	for port, io in [('x-touch-in', 'in'), ('x-touch-out', 'out'), ('loopmidi-in', 'in'), ('loopmidi-out', 'out')]:
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



if __name__ == '__main__':
	try:
		pygame.init()
		pygame.midi.init()

		midi_connect()
		print('\ndevices_info:')
		pprint(devices_info)

	except KeyboardInterrupt:
		pass
	finally:
		
		if devices_info['x-touch-in'][0]: devices_info['x-touch-in'][0].close()
		if devices_info['x-touch-out'][0]: devices_info['x-touch-out'][0].close()
		if devices_info['loopmidi-in'][0]: devices_info['loopmidi-in'][0].close()
		if devices_info['loopmidi-out'][0]: devices_info['loopmidi-out'][0].close()

		pygame.midi.quit()
		pygame.quit()