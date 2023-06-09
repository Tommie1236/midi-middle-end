from termcolor import colored
# import subprocess
from segments import SEGMENTS # 7-segment data
import pygame.midi
import pygame
import os
import time

def debounce(lst):
	result = []
	for i in range(len(lst)):
		if i == 0 or lst[i] != lst[i-1]:
			result.append(lst[i])
	return result

class XTouch:

	def __init__ (self, ip_port, op_port):
		self.input  : pygame.midi.Input  = pygame.midi.Input (ip_port)
		self.output : pygame.midi.Output = pygame.midi.Output(op_port)
		self.segments = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self.dots = [0b0000000, 0b00000]

	def close(self):
		self.input.close()
		self.output.close()

	def send_midi(self, type: str, data: list):
		types = {
			'note_on': 0x90,
			'note_off': 0x80,
			'control_change': 0xb0}
		if type.lower() == 'sysex':
			self.send_sysex(data)
		else:
			try:
				self.output.write([[[types[type.lower()], *data], pygame.midi.time()]])
			except:
				self.error(f'midi data <{[type, *data]}> not send')

	def send_sysex(self, data):
			self.output.write_sys_ex(pygame.midi.time(), data)
	
	def update_segment_display(self):
		print(self.segments)
		self.send_sysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x37, *self.segments, *self.dots, 0xf7])

	def set_segment_data(self, idx: int, chars: str):
		'''
		sets the segment data to something
		args: 
		- idx, the index of the segment you want to updated. (0-11)
		- chars, the charachers you want to put 
		'''
		if idx < 0 or idx > 11:
			self.error(f'segment index <{idx}> out of range, needs to be 0-11.')
			return False
		if idx + len(chars) > 12:
			self.warning(f"chars: <{chars}> doesn't fit in the display, characthers are cut off.")
		for char in chars:
			char = char.lower()
			if char in SEGMENTS.keys():
				self.segments[idx] = SEGMENTS[char]
			else:
				self.warning(f'char <{char}> not a valid segment characther')
			idx += 1


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
			self.send_midi('note_on', [i, 0])
			self.send_midi('control_change', [i, 0])

	def led_on(self, *numbers):
		for number in numbers:
			if number >= 0 and number <= 93:
				self.send_midi('note_on', [number+8, 127])
			else:
				self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')
	
	def led_off(self, *numbers):
		for number in numbers:
			if number >= 0 and number <= 93:
				self.send_midi('note_on', [number+8, 0])
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
			self.send_midi('control_change', [i + 70, 127])
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
		
	def send_midi(self, type, data):
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



if __name__ == '__main__':
	try:
		pygame.init()
		pygame.midi.init()

		xt = XTouch(1,6)
		md = MyDmx(4,8)
		# uncomment below if you want to launch mydmx
		# os.startfile(r'C:\Users\Licht computer\Desktop\licht-files\aula_v_8.0.dvc')

		# startup sequence
		xt.led_all_on()
		xt.all_faders_up()
		time.sleep(.5)
		xt.reset_controls()

		xt.set_segment_data(0, '0123456789ab')
		xt.update_segment_display()
		
		# just send everyting to the other midi port
		while True:
			d = xt.get_data()
			if d: print(d)
			for m in d:
				md.send_midi(m[0], m[1:])
			
			e = md.get_data()
			if e: print(e)
			for m in e:
				xt.send_midi(m[0], m[1:])

	finally:
		try:
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