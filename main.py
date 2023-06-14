import argparse
import os
import time
import json

import keyboard
import pygame
import pygame.midi
from termcolor import colored

from segments import SEGMENTS  # 7-segment data

KEYS = {96: 'up',
		97: 'down',
		98: 'left',
		99: 'right'}
ENCODERS = [0, 0, 0 ,0 ,0 ,0 ,0 ,0]
COLORS = {
		'black'	 : 0b000,
		'red'	 : 0b001,	
		'green'	 : 0b010,
		'yellow' : 0b011,
		'blue'	 : 0b100,
		'magenta': 0b101,
		'cyan'	 : 0b110,
		'white'	 : 0b111}



def debounce(lst):
	result = []
	for i in range(len(lst)):
		if i == 0 or lst[i] != lst[i-1]:
			result.append(lst[i])
	return result

def setup_midi():
	dev_count = pygame.midi.get_count()
	if dev_count == 0: print('No MIDI devices found, exiting program.'); exit()

	print('Available MIDI devices:')
	for i in range(dev_count):
		print(f'[{i:2}] - {pygame.midi.get_device_info(i)[1].decode("utf-8")}')
	
	ports = []
	for port in [('x-touch-in', 'in'), ('x-touch-out', 'out'), ('MyDmx-in (mydmx - python)', 'in'), ('MyDmx-out (python - mydmx)', 'out')]:
		while True:
			try:
				i = int(input(f'Enter index of <{port[0]}>: '))
				if 0 <= i < dev_count:
					ports[port] = i
					break
				else:
					print('Invalid MIDI device index. Try again.')
			except ValueError:
				print('Invalid index input. Please enter a valid index (integer).')
		return tuple(ports)
		
def setup_argparser():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', "--default-ports", action='store_true', help='use the default midi ports (xtouch 1, 6 mydmx 4, 8)') 
	return parser.parse_args()



class XTouch:
	def __init__ (self, ip_port, op_port):
		"""Initiate a connection with the 'behringer x-touch one' MIDI controller"""
		self.ip_port = ip_port
		self.op_port = op_port
		self.input  : pygame.midi.Input  = pygame.midi.Input (self.ip_port)	# connect to MIDI in port of x-touch
		self.output : pygame.midi.Output = pygame.midi.Output(self.op_port)	# connect to MIDI out port of x-touch
		self.segments = [0x00 for _ in range(12)]							# set segment display data to all off
		self.dots = [0b0000000, 0b00000]									# set segment dots to all off
		self.strips1 = [[0x00 for _ in range(7)] for _ in range(8)]			# create list of 8 displays of 7 chars (top display)
		self.strips2 = [[0x00 for _ in range(7)] for _ in range(8)]			# create list of 8 displays of 7 chars (bottom display)
		self.backlight = [0b000000 for _ in range(8)]						# create list of 8x 0b00000 for backlight
		self.channelbank = 0 												# set the channel-bank to 0
		self.presetsbank = 0 												# set the presets-bank to 0
		self.mode = 'channel'												# set mode to channel
		self.leds = [0 for _ in range(93)]									# create a list of 93 zeroes

	def close(self):
		"""close the MIDI ports"""
		self.input.close()
		self.output.close()

	def connect(self):
		"""Connect to the x-touch midi controller.
		Not needed unless you closed the connection.
		"""
		self.input  = pygame.midi.Input (self.ip_port)
		self.output = pygame.midi.Output(self.op_port)

	def _send_midi(self, type: str, data: list):
		"""Sends midi message to x-touch controller
		Args:
		- type (str)	Type of the MIDI message ('note_on', 'note_off', 'control_change')
		- data (list)	A list of bytes to send to the MIDI controller.
		"""
		types = {
			'note_on': 0x90,
			'note_off': 0x80,
			'control_change': 0xb0}
		if type.lower() == 'sysex':
			self._send_sysex(data)
		else:
			try:
				self.output.write([[[types[type.lower()], *data], pygame.midi.time()]])
			except:
				self.error(f'midi data <{[type, *data]}> not send')

	def _send_sysex(self, data: bytes):
		"""Send a SysEx message to the MIDI controller.
		Used in for example updating the 7-segment displays and LCD-Scribble-strips.
		Args:
		- data (bytes)	The data you want to send to the MIDI controller
		"""
		self.output.write_sys_ex(pygame.midi.time(), data)
	
	def update_segment_display(self):
		"""Update the 7-segment displays to the data in self.segments
		Use the XTouch.set_segment_data() function to set the segment data
		"""
		self._send_sysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x37, *self.segments, *self.dots, 0xf7])

	def clear_segments_display(self):
		"""Clear (and update) the 7-segment displays.
		"""
		self.segments = [0x00 for _ in range(12)]		# create list of 12 times 0x00
		self.update_segment_display()

	def set_segment_data(self, idx: int, chars: str):
		'''Sets the segment data to something
		Args: 
		- idx 	(int) The index of the segment you want to (start) update. (0-11)
		- chars (str) The characher(s) you want to put at the specified index.
		'''
		if not isinstance(idx, int):	self.warning(f'index needs to be a integer.')												# check if idx is a integer
		if idx < 0 or idx > 11:			self.error(f'segment index <{idx}> out of range, needs to be 0-11.'); return 				# check if idx is in range
		if idx + len(chars) > 12:		self.warning(f"chars: <{chars}> doesn't fit in the display, characthers are cut off.")		# check if chars fit on screen
		
		for char in chars:
			if idx > 11:	break
			char = char.lower()

			if char in SEGMENTS.keys():
				self.segments[idx] = SEGMENTS[char]
				# first clear the dot at a specified index
				if idx < 7:	self.dots[0] &= 0b0 << idx
				else:		self.dots[1] &= 0b0 << (idx - 7)

			elif char == '.': 	# then activate the dot if it needs to be activated
				if idx < 7:	self.dots[0] |= 0b1 << idx
				else:		self.dots[1] |= 0b1 << (idx - 7)
				continue	# skip incrementing the idx var to not skip the next segment because the dot is in the same segment as the last char

			else:	self.warning(f'char <{char}> not a valid segment characther')
			idx += 1

		self.update_segment_display()

	def update_scribble_strip(self, display: int):			# TODO docstring and comments
		if display < 0 or display > 7:
			self.error(f'Display <{display}> not valid. (0-7)\nData not send!')
			return
		self._send_sysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x4c, display, self.backlight[display], *self.strips1[display], *self.strips2[display], 0xf7])

	def set_scribble_strip_color(self, display: int, color: str, inv_top: bool = False, inv_bottom: bool = False):	# TODO docstring and comments
		""" backlight
		0bxxxyz
		xxx - color
		000 - black
		001 - red
		010 - green
		011 - yellow
		100 - blue
		101 - magenta
		110 - cyan
		111 - white

		y - invert top
		z - invert bottom
		"""
		self.backlight[display] = 0b00000
		self.backlight[display] |= COLORS[color] << 0
		self.backlight[display] |= inv_top << 4
		self.backlight[display] |= inv_bottom << 5

	def clear_scribble_strip(self, display: int):	# TODO docstring and comments
		self.strips1[display] = [0b00 for _ in range(7)]
		self.strips2[display] = [0b00 for _ in range(7)]
		self.update_scribble_strip(display)

	def clear_scribble_strips(self):	# TODO docstring and comments
		for i in range(8):
			self.clear_scribble_strip(i)

	def set_scribble_strip_data(self, display: int, topidx: int, topchars: str, bottomidx: int, bottomchars: str):	# TODO docstring and comments
		# set top display data
		if not isinstance(topidx, int): self.warning(f'Topidx needs to be a integer.')
		if topidx < 0 or topidx > 7: self.error(f'Character index <{topidx}> out of range. (0-7)')
		if topidx + len(topchars) > 14: self.warning(f"Topchars: <{topchars}> doesn't fit in the display, characthers are cut off.")
		
		for char in topchars:
			if topidx > 7: break
			self.strips1[display][topidx] = ord(char)
			topidx += 1
		
		if not isinstance(bottomidx, int): self.warning(f'Bottomidx needs to be a integer.')
		if bottomidx < 0 or bottomidx > 7: self.error(f'Character index <{bottomidx}> out of range. (0-7)')
		if bottomidx + len(bottomchars) > 14: self.warning(f"Bottomchars: <{bottomchars}> doesn't fit in the display, characthers are cut off.")
		
		for char in bottomchars:
			if bottomidx > 7: break
			self.strips2[display][bottomidx] = ord(char)
			bottomidx += 1

		self.update_scribble_strip(display)

	def update_bank(self ,change: int):	# TODO docstring and comments
		bank = getattr(self, f'{self.mode}bank')
		bank += change
		if bank < 0: bank = 99
		if bank > 99: bank = 0
		setattr(self, f'{self.mode}bank', bank)
		self.set_segment_data(0, f'{bank:02d}')
		
		# old one bank system below, maybe handy later to look back on. isn't needed in production anymore
		# self.banknr += change
		# if self.banknr < 0: self.banknr = 99
		# if self.banknr > 99: self.banknr = 0
		# self.set_segment_data(0, f'{self.banknr:02d}')
		# print(colored(f'Bank set to: {self.banknr:02d}', 'green'))

	def set_bank_nr(self, bank: str, number: int):	# TODO docstring and comments
		if bank == 'channels':
			self.channelbank = number
			self.set_segment_data(0, f'{self.channelbank:02d}')
		elif bank == 'presets':
			self.presetsbank = number
			self.set_segment_data(0, f'{self.presetsbank:02d}')

	def update_mode(self, mode = None):	# TODO docstring and comments
		if mode: self.mode = mode
		if self.mode == 'channel':
			self.led_on(86)
			self.led_off(87)
			self.set_segment_data(0, f'{self.channelbank:02d}')
		elif self.mode == 'presets':
			self.led_on(87)
			self.led_off(86)
			self.set_segment_data(0, f'{self.presetsbank:02d}')
		self.set_segment_data(2, f'{self.mode:7}')

	def get_data(self) -> list:	# TODO docstring and comments
		types = {
			0x90: 'note_on',
			0x80: 'note_off',
			0xb0: 'control_change'}

		data_in = self.input.read(10)
		data = [[types[d[0][0]], *d[0][1:]] for d in data_in]

		# compressed into list comprehention but if it gets problems the working code is commented below

		# for d in data_in:
		# 	m = d[0]
		# 	t = types[m[0]]
		# 	data.append([t, *m[1:]])

		return debounce(data)
			
	def reset_controls(self):	# TODO docstring and comments
		for i in range(119):
			self._send_midi('note_on', [i, 0])
			self._send_midi('control_change', [i, 0])

	def led_on(self, *numbers):	# TODO docstring and comments
		for number in numbers:
			if number >= 0 and number <= 93:
				self._send_midi('note_on', [number+8, 127])
				self.leds[number] = 1
			else:
				self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')
	
	def led_off(self, *numbers):	# TODO docstring and comments
		for number in numbers:
			if number >= 0 and number <= 93:
				self._send_midi('note_on', [number+8, 0])
				self.leds[number] = 0
			else:
				self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')
		
	def led_toggle(self, *numbers):	
		"""Toggles the specified LED(S)
		Args:
		- number (int | list) The LED(S) you want to toggle on/off. (0-93)
		"""
		for number in numbers:
			if   self.leds[number] == 0:	self.led_on (number);	self.leds[number] = 1 	# Toggle on
			elif self.leds[number] == 1:	self.led_off(number);	self.leds[number] = 0 	# Toggle off

	def led_all_off(self):	# TODO docstring and comments
		for i in range(94):
			self.led_off(i)

	def led_all_on(self):	# TODO docstring and comments
		for i in range(94):
			self.led_on(i)
	
	def all_faders_up(self):	# TODO docstring and comments
		for i in range(20):
			self._send_midi('control_change', [i + 70, 127])
			time.sleep(.05)

	def error(self, message: str):	# TODO docstring and comments
		print(colored(f'ERROR: {message}', 'white', 'on_red'))

	def warning(self, message: str):	# TODO docstring and comments
		print(colored(f'WARNING: {message}', 'white', 'on_blue'))

class MyDmx:	# TODO docstring and comments
	def __init__(self, ip_port, op_port):
		self.input  : pygame.midi.Input  = pygame.midi.Input (ip_port)
		self.output : pygame.midi.Output = pygame.midi.Output(op_port)

	def close(self):
		self.input.close()
		self.output.close()
		
	def _send_midi(self, type, data):
		types = {
			'note_on': 0x90,
			'note_off': 0x80,
			'control_change': 0xb0}
		try: 
			self.output.write([[[types[type], *data], pygame.midi.time()]])
		except:
			self.error(f'midi data <{[type, *data]}> not send')

	def get_data(self) -> list:
		types = {
			0x90: 'note_on',
			0x80: 'note_off',
			0xb0: 'control_change'}
		
		data_in = self.input.read(10)
		data = [[types[d[0][0]], *d[0][1:]] for d in data_in]

		# compressed into list comprehention but if it gets problems the working code is commented below

		# for d in data_in:
		# 	m = d[0]
		# 	t = types[m[0]]
		# 	data.append([t, *m[1:]])
		
		return debounce(data)

	def error(self, message):
		print(colored(f'ERROR: {message}', 'white', 'on_red'))

	def warning(self, message):
		print(colored(f'WARNING: {message}', 'white', 'on_blue'))

class BPM:	# TODO docstring and comments
	def __init__(self):
		self.bpm = 0
		self.maxdata = 2
		self.data = []

	def bpm_pulse(self):
		self.data.append(time.time())
		self.data = self.data[-self.maxdata:]

	def calculate_bpm(self) -> int:
		between = round((self.data[-1]	- self.data[0]), 2)
		if between > 2: return
		try:
			self.bpm = int((1 / between) * 60)
			# print(f'{between:5} {len(self.data):2} {self.bpm} {self.data}')
		except: pass
		xt.set_segment_data(9, f'{self.bpm:03d}')
	
class Presets:	# TODO docstring and comments
	def __init__(self):
		self.data = {}

	def load(self, file: str = 'presets.json'):
		self.file = file
		with open(self.file, 'r') as file:
			self.data = json.load(file)

	def save(self, file: str, indent: int = 4):
		if file:
			with open(file, 'w') as file:
				json.dump(self.data, file, indent)
		else:
			with open(self.file. 'w') as file:
				json.dump(self.data, file, indent)

	def get_channel(self, bank: int, channel: int):
		self.data[]


if __name__ == '__main__':
	try:
		args = setup_argparser()
		pygame.init()
		pygame.midi.init()
		if args.default_ports:
			print(colored('Using default MIDI ports: (xtouch 1, 6 mydmx 4, 8).', 'white', 'on_green'))
			xt = XTouch(1,6)
			md = MyDmx (4,8)
		else:
			ports: tuple = setup_midi()
			print(ports)
			xt = XTouch(*ports[0:2])
			md = MyDmx (*ports[2:4])
		bpm = BPM()
		bpm.bpm_pulse()
		# uncomment below if you want to launch mydmx
		# os.startfile(r'C:\Users\Licht computer\Desktop\licht-files\aula_v_8.0.dvc')

		# startup sequence
		xt.led_all_on()
		xt.all_faders_up()
		xt.set_segment_data(0, '0123456789ab')
		time.sleep(.5)
		xt.reset_controls()
		xt.clear_segments_display()

		xt.set_bank_nr('channel', 0)
		xt.set_bank_nr('presets', 0)
		xt.update_mode()


		xt.update_segment_display()
		# Code in 3 lines below only for testing. Remove later.
		for i in range(7):
			xt.set_scribble_strip_color(i, 'white')
			xt.set_scribble_strip_data(0, 0, 'Display', 0, f'{i}')




		# just send everyting to the other midi port
		while True:
			d = xt.get_data()
			if d:
				print(d)
				for m in d:
					if m[0] == 'note_on':
						match m[1]:
							case 92:	# bankdown button
								if m[2] == 127: xt.update_bank(-1); xt.led_on(84)
								elif m[2] == 0: xt.led_off(84)
								continue 
							case 93:	# bankup button
								if m[2] == 127: xt.update_bank(1); xt.led_on(85)
								elif m[2] == 0: xt.led_off(85)
								continue
							case 94:	# channels button
								xt.update_mode('channel')
								continue
							case 95: 	# presets button
								xt.update_mode('presets')
								continue
							case 101:	# bpm button
								if m[2] == 127:
									xt.led_on(93)
									bpm.bpm_pulse()
									bpm.calculate_bpm()
								elif m[2] == 0:	xt.led_off(93)
								continue							

						if m[1] in [96, 97, 98, 99]:
							if m[2] == 127:
								xt.led_on(m[1] - 8)
								keyboard.press(KEYS[m[1]])
							elif m[2] == 0:
								xt.led_off(m[1] - 8)
								keyboard.release(KEYS[m[1]])
							continue	

					if m[0] == 'control_change':
						match m[1]:
							case 64:
								if m[2] in [0, 48]:
									xt.led_on(93)
									bpm.bpm_pulse()
									bpm.calculate_bpm()
								elif m[2] in [127, 175]:
									xt.led_off(93)
								continue
							case 88:
								if m[2] == 65:
									xt.update_bank(1)
								elif m[2] == 1:
									xt.update_bank(-1)
								continue

						if m[1] in [80, 81, 82, 83, 84, 85, 86, 87]:
							if m[2] == 1:
								ENCODERS[m[1] - 80] -= 9
							elif m[2] == 65:
								ENCODERS[m[1] - 80] += 9
							ENCODERS = [max(0, min(value, 127)) for value in ENCODERS] # cap the values in the list between 0 and 127
							continue

			e = md.get_data()
			if e:
				print(e)
				for m in e:
					...

	finally:
		try:
			xt.clear_segments_display()
			xt.reset_controls()
			xt.close()
			md.close()
		except:
			pass
		finally:
			pygame.midi.quit()
			pygame.quit()
			# uncomment below if you want the mydmx closing warnings
			# os.system(r'msg * Please close and save changes in the MyDMX software')
			# print(colored('Please close and save changes in the MyDMX software.', 'white', 'on_red'))