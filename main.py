from termcolor import colored
# import subprocess
from segments import SEGMENTS # 7-segment data
import pygame.midi
import pygame
import argparse
import os
import time

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
				i = int(input(f'Enter index of <{port}>: '))
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
		self.input  : pygame.midi.Input  = pygame.midi.Input (ip_port)
		self.output : pygame.midi.Output = pygame.midi.Output(op_port)
		self.segments = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self.dots = [0b0000000, 0b00000]
		self.banknr = 0
		self.mode = 'channel'

	def close(self):
		self.input.close()
		self.output.close()

	def _send_midi(self, type: str, data: list):
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

	def _send_sysex(self, data):
			self.output.write_sys_ex(pygame.midi.time(), data)
	
	def update_segment_display(self):
		# print(self.segments)
		self._send_sysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x37, *self.segments, *self.dots, 0xf7])

	def clear_segments_display(self):
		self.segments = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self.update_segment_display()

	def set_segment_data(self, idx: int, chars: str):
		'''
		sets the segment data to something
		args: 
		- idx, the index of the segment you want to updated. (0-11)
		- chars, the charachers you want to put 
		'''
		if not isinstance(idx, int):
			self.warning(f'index needs to be a integer.')
		if idx < 0 or idx > 11:
			self.error(f'segment index <{idx}> out of range, needs to be 0-11.')
			return False
		if idx + len(chars) > 12:
			self.warning(f"chars: <{chars}> doesn't fit in the display, characthers are cut off.")
		for char in chars:
			if idx > 11:
				break
			char = char.lower()
			if char in SEGMENTS.keys():
				self.segments[idx] = SEGMENTS[char]
				# first clear the dot at a specified index
				if idx < 7:
					self.dots[0] &= 0b0 << idx
				else:
					self.dots[1] &= 0b0 << (idx - 7)
			elif char == '.': 	# then activate the dot if it needs to
				if idx < 7:
					self.dots[0] |= 0b1 << idx
				else:
					self.dots[1] |= 0b1 << (idx - 7)
				continue	# skip incrementing the idx var to not skip the next segment because the dot is in the same segment as the last char
			else:
				self.warning(f'char <{char}> not a valid segment characther')
			idx += 1
		self.update_segment_display()

	def update_bank(self, change):
		self.banknr += change
		if self.banknr < 0: self.banknr = 99
		if self.banknr > 99: self.banknr = 0
		self.set_segment_data(0, f'{self.banknr:02d}')
		print(colored(f'Bank set to: {self.banknr:02d}', 'green'))

	def set_bank_nr(self, number):
		self.banknr = number
		self.set_segment_data(0, f'{self.banknr:02d}')

	def update_mode(self, mode):
		self.mode = mode
		self.set_segment_data(2, f'{mode:7}')

	def get_data(self) -> list:
		types = {
			0x90: 'note_on',
			0x80: 'note_off',
			0xb0: 'control_change'}

		data_in = self.input.read(10)
		data= []
		for d in data_in:
			m = d[0]
			t = types[m[0]]

			data.append([t, *m[1:]])
		return debounce(data)
			
	def reset_controls(self):
		for i in range(119):
			self._send_midi('note_on', [i, 0])
			self._send_midi('control_change', [i, 0])

	def led_on(self, *numbers):
		for number in numbers:
			if number >= 0 and number <= 93:
				self._send_midi('note_on', [number+8, 127])
			else:
				self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')
	
	def led_off(self, *numbers):
		for number in numbers:
			if number >= 0 and number <= 93:
				self._send_midi('note_on', [number+8, 0])
			else:
				self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')
		
	def led_all_off(self):
		for i in range(94):
			self.led_off(i)

	def led_all_on(self):
		for i in range(94):
			self.led_on(i)
	
	def all_faders_up(self):
		for i in range(20):
			self._send_midi('control_change', [i + 70, 127])
			time.sleep(.1)

	def error(self, message):
		print(colored(f'ERROR: {message}', 'white', 'on_red'))

	def warning(self, message):
		print(colored(f'WARNING: {message}', 'white', 'on_blue'))

class MyDmx:
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
		data= []
		for d in data_in:
			m = d[0]
			t = types[m[0]]

			data.append([t, *m[1:]])
		
		return debounce(data)

	def error(self, message):
		print(colored(f'ERROR: {message}', 'white', 'on_red'))

	def warning(self, message):
		print(colored(f'WARNING: {message}', 'white', 'on_blue'))

class BPM:
	def __init__(self):
		self.bpm = 0
		self.maxdata = 2
		self.data = []

	def bpm_pulse(self):
		self.data.append(time.time())
		self.data = self.data[-self.maxdata:]

	def calculate_bpm(self) -> int:
		between = round((self.data[-1]	- self.data[0]), 2)
		try:
			self.bpm = int((1 / between) * 60)
			# print(f'{between:5} {len(self.data):2} {self.bpm} {self.data}')
		except: pass
		return f'{self.bpm:03d}'
	



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
			exit()
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

		xt.set_bank_nr(0)


		xt.update_segment_display()
		
		# just send everyting to the other midi port
		while True:
			d = xt.get_data()
			if d:
				print(d)
				for m in d:
					if m[0] == 'note_on' and m[2] == 127:
						match m[1]:
							case 92:	# bankdown button
								xt.update_bank(-1)
								continue
							case 93:	# bankup button
								xt.update_bank(1)
								continue
							case 94:	# channels button
								xt.update_mode('channel')	
								continue
							case 95: 	# presets button
								xt.update_mode('presets')
								continue
							case 101:	# bpm button
								bpm.bpm_pulse()
								xt.set_segment_data(9, bpm.calculate_bpm())
								continue


					# md._send_midi(m[0], m[1:]) # uncomment to send all midi data to mydmx3

			e = md.get_data()
			if e:
				print(e)
				for m in e:
					...
					# xt._send_midi(m[0], m[1:]) # uncomment to send all midi data to x-touch

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