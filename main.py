from termcolor import colored
import pygame.midi
import pygame
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

	def send_midi(self, type, data):
		types = {
			'note_on': 0x90,
			'note_off': 0x80,
			'control_change': 0xb0}
		try:
			self.output.write([[[types[type], *data], pygame.midi.time()]])
		except:
			self.error(f'midi data <{[type, *data]}> not send')


	def send_sysex(self, data):
		...
	
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
			
	def led_on(self, number):
		if number > 0 and number <= 93:
			self.send_midi('note_on', [number+8, 127])
		else:
			self.warning(f'Button <{number}> is not valid, must be greater than 0 and cant be greater than 93')

	def error(self, message):
		print(colored(f'ERROR: {message}', 'white', 'on_red'))

	def warning(self, message):
		print(colored(f'WARNING: {message}', 'white', 'on_blue'))

class MyDmx:
	def __init__(self, ip_port, op_port):
		self.input  : pygame.midi.Input  = pygame.midi.Input (ip_port)
		self.output : pygame.midi.Output = pygame.midi.Output(op_port)
		

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


pygame.init()
pygame.midi.init()
xt = XTouch(1,6)
md = MyDmx(3,8)

# for i in range(127):
#     xt.send_midi('note_on', [i, 127])
#     xt.send_midi('control_change', [i, 127])
#     time.sleep(.1)


# print(debounce([3, 3, 3, 4, 6, 6, 7]))

while True:
	d = xt.get_data()
	if d: print(d)
	for m in d:
		md.send_midi(m[0], m[1:])
	
	e = md.get_data()
	if e: print(e)
	for m in e:
		xt.send_midi(m[0], m[1:])
