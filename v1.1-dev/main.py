import argparse
import json
import platform
import time
from dataclasses import dataclass

import keyboard
import pygame
import pygame.midi
from termcolor import colored

# import helper data/constants/functions
from helper import SEGMENTS, COLORS, MIDITYPES, centerString 	 
		# - 7-segment display chars
		# - backlight colors
		# - midi message types
		# - string centering function




# main classes

class MidiDevice:
	_output: pygame.midi.Output
	_input: pygame.midi.Input
	device: str

	def __init__(self) -> None:
		pass

	def connect(self, ipPort, opPort) -> None:
		self.ipPort, self.opPort = ipPort, opPort
		self._input  = pygame.midi.Input (ipPort)
		self._output = pygame.midi.Output(opPort)

	def close(self) -> None:
		self._input .close()
		self._output.close()

	def _sendMidi(self, type: str, data: list) -> None:
		if type.lower() == 'sysex':
			self._sendSysex(data)
		else:
			try:
				self._output.write([[[MIDITYPES[type.lower()], *data], pygame.midi.time()]])
			except:
				self.error(f'midi data <{[type, *data]}> not send')
	
	def _sendSysex(self, data: bytes) -> None:
		"""Send a SysEx message to the MIDI controller.
		Used in for example updating the 7-segment displays and LCD-Scribble-strips.
		Args:
		- data (bytes)	The data you want to send to the MIDI controller
		"""
		self._output.write_sys_ex(pygame.midi.time(), data)

	def getData(self) -> list:
		dataIn = self._input.read(10) # change if needed
		data = [[MIDITYPES[d[0][0]], *d[0][1]] for d in dataIn]
		return self._debounce(data) 

	def _debounce(lst) -> list:
		return [lst[i] for i in range(len(lst)) if i == 0 or lst[i] != lst[i-1]]
		# old list comprehention below for readability and in case of broken comprehention
		# result = []
		# for i in range(len(lst)):
		# 	if i == 0 or lst[i] != lst[i-1]:
		# 		result.append(lst[i])
	
	def error(self, message: str) -> None:	# TODO docstring and comments
		print(colored(f'ERROR   {self.device: 10}: {message}', 'white', 'on_red'))

	def warning(self, message: str) -> None:	# TODO docstring and comments
		print(colored(f'WARNING {self.device: 10}: {message}', 'white', 'on_blue'))

class XTouch(MidiDevice):
	def __init__(self) -> None:
		super().__init__()
		self.segments = [0x00 for _ in range(12)]									# set segment display data to all clear
		self.dots = [0b0000000, 0b00000]
		self.stripsTop    = [[0x00 for _ in range(7)] for _ in range(8)]			# create list of 8 displays of 7 chars (top display)
		self.stripsBottom = [[0x00 for _ in range(7)] for _ in range(8)]			# create list of 8 displays of 7 chars (bottom display)
		self.stripsBacklight = [0b000000 for _ in range(8)]							# create list of 8x 0b00000 for backlight
		self.channelBank = 0
		self.presetsBank = 0
		self.mode = 'channel'
		self.leds = [0b0 for _ in range(94)]

		self.encoders = [Encoder(chn) for chn in range(8)]

	# 7-Segment display methods
	def updateSegmentDisplay(self) -> bool:
		try:
			self._sendSysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x37, *self.segments, *self.dots, 0xf7])
			return True
		except Exception as e:
			self.error(f'Exception <{e}> raised while trying to update the 7-Segment displays.')
			return False

	def clearSegmentDisplay(self) -> bool:
		self.segments = [0x00 for _ in range(12)]
		return self.updateSegmentDisplay()

	def setSegmentData(self, idx: int, chars: str) -> bool:

		if not isinstance(idx, int):	self.error  (f'Index needs to be a integer.'); return False
		if idx < 0 or idx > 11: 		self.error  (f'Index <{idx}> out of range. (0-11)'); return False
		if idx + len(chars) > 12:		self.warning(f"String <{chars}> doesn't fit and will be cut off")

		for char in chars:
			if idx > 11: break
			char = char.lower()

			# set the display to the current char and clear the dot at that index
			if char in SEGMENTS.keys():
				self.segments[idx] = SEGMENTS[char]
				if idx < 7: self.dots[0] &= 0b0 <<  idx
				else: 		self.dots[1] &= 0b0 << (idx - 7)

			# activate the dot again if there is a . in the chars string
			elif char == '.':
				if idx < 7: self.dots[0] |= 0b1 <<  idx
				else:		self.dots[1] |= 0b1 << (idx-7)
				continue	# The dot is in the same segment as the last char so don't increment and don't skip the next char 

			else:	self.error(f'Char <{char}> is not a valid segment characther.')
			idx += 1

		self.updateSegmentDisplay() # update the display to the new data
		return True

	# LCD Scribble strips methods
	def updateScribbleStrip(self, display: int) -> bool:
		if display < 0 or display > 7:
			self.error(f'Display <{display}> out of range. (0-7)\nDisplay not updated!')
			return False
		self._sendSysex([0xf0, 0x00, 0x20, 0x32, 0x14, 0x4c, display, self.stripsBacklight[display], *self.stripsTop[display], *self.stripsBottom[display], 0xf7])
		return True

	def setScibbleStripBacklight(self, display: int, color: str, invTop: bool = False, invBottom: bool = False) -> bool:
		""" backlight
		0bxyzzz
		zzz - color
		000 - black
		001 - red
		010 - green
		011 - yellow
		100 - blue
		101 - magenta
		110 - cyan
		111 - white

		y - invert top
		x - invert bottom
		"""
		self.stripsBacklight[display] = COLORS[color.lower()] | (invTop << 4) | (invBottom << 5)
		return self.updateScribbleStrip(display)

	def clearScribbleStrip(self, display: int) -> bool:
		self.stripsTop   [display] = [0x00 for _ in range(7)]
		self.stripsBottom[display] = [0x00 for _ in range(7)]
		return self.updateScribbleStrip(display)
	
	def clearScribbleStrips(self) -> bool:
		for i in range(8):
			self.clearScribbleStrip(i)
		return True

	def resetScribbleStrips(self) -> bool:
		for i in range(8):
			self.setScibbleStripBacklight(i, 'white')
			self.clearScribbleStrip(i)
		return True
	
	def setScribbleStripData(self, display: int, topChars: str = None, bottomChars: str = None) -> bool:
		# Top row
		if isinstance(topChars, str):
			topChars = centerString(topChars)

			for topIdx, char in enumerate(topChars):
				self.stripsTop[display][topIdx] = ord(char)
		
		else:
			self.error(f"'topChars' needs to be of type str, not {type(topChars)}.")

		# Bottom row
		if isinstance(bottomChars, str):
			bottomChars = centerString(bottomChars)

			for bottomIdx, char in enumerate(bottomChars):
				self.stripsBottom[display][bottomIdx] = ord(char)

		return self.updateScribbleStrip(display)
	
	# bank and mode methods
	def updateBank(self, change: int):
		bank = getattr(self, f'{self.mode}bank')
		bank += change
		if self.mode == 'presets':
			if bank < 0 : bank = 99
			if bank > 99: bank = 0
		if self.mode == 'channel':
			if bank < 0 : bank = 63
			if bank > 63: bank = 0
		setattr(self, f'{self.mode}bank', bank)
		print(f'{self.mode}bank = {bank}')
		self.setSegmentData(0, f'{bank:02d}')

	def setBankNr(self, number: int, bank: str = None):
		# if bank specified set that bank to number
		if bank: setattr(self, f'{bank}bank', 	   number)
		else:	 setattr(self, f'{self.mode}bank', number)

		self.setSegmentData(0, f'{getattr(self, f"{self.mode}bank"):02d}')

	def updateMode(self, mode: str):
		if mode in ['channel', 'presets']: 
			self.mode = mode
		match self.mode:
			case 'channel':
				self.ledOn (86)
				self.ledOff(87)
			case 'presets':
				self.ledOn (87)
				self.ledOff(86)
		self.setSegmentData(0, f'{getattr(self, f"{self.mode}bank"):02d}{self.mode:7}')
	
	# LED methods

	def ledOn(self, *leds):
		for led in leds:
			if led >= 0 and led <= 93:
				self._sendMidi('note_on', [led+8, 127])
				self.leds[led] =0b1
			else:
				self.warning(f'Button <{led}> is not valid, must be between 0 and 93')

	def ledAllOn(self):
		for i in range(94):
			self.ledOn(i)

	def ledOff(self, *leds):
		for led in leds:
			if led >= 0 and led <= 93:
				self._sendMidi('note_on', [led+8, 0])
				self.leds[led] = 0b0
			else:
				self.warning(f'Button <{led}> is not valid, must be between 0 and 93')

	def ledAllOff(self):
		for i in range(94):
			self.ledOff(i)

	def ledToggle(self, *leds):
		for led in leds:
			self.leds[led] = not self.leds[led]
			self._sendMidi('note_on', [led+8, self.leds[led] * 127])

	def resetControls(self):
		for i in range(119):
			self._sendMidi('note_on', [i, 0])
			self._sendMidi('control_change', [i, 0])
	
	def startUpSequence(self):
		self.ledAllOn()
		for i in range(20):
			self._sendMidi('control_change', [i + 70, 127])
			time.sleep(.05)
		self.setSegmentData(0, '0123456789ab')
		for i, c in enumerate(list(COLORS.keys())[1:]):
			self.setScibbleStripBacklight(i, c)
			self.setScribbleStripData(i, 'Display', f'{i}')
		time.sleep(2)
		self.resetControls()
		self.clearSegmentDisplay()
		self.resetScribbleStrips()
	
	# 

class MyDmx3(MidiDevice):
	def __init__(self) -> None:
		super().__init__()

	# def togglePreset(self):
	# 	...

	def setChannel(self, channel, value):
		self._sendMidi('control_change', [])



# helper classes

class Encoder:
	value: int
	channel: int

	def __init__(self, channel) -> None:
		self.channel = channel
		self.value = 0

	def updateValue(self, value):
		self.value += value
		
	def getValue(self):
		return self.value
	
	def __str__(self) -> str:
		return f'ENCODER instance, channel = {self.channel}, value = {self.value}'

	def __repr__(self) -> str:
		return f'ENCODER({self.channel}, {self.value})'

def setupMidi() -> tuple:
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
					ports.append(i)
					break
				else:
					print('Invalid MIDI device index. Try again.')
			except ValueError:
				print('Invalid index input. Please enter a valid index (integer).')
	return tuple(ports)



class Main():
	def __init__(self) -> None:
		pass

	def go(self):
		if platform.system() == 'Windows':
			from colorama import just_fix_windows_console
			just_fix_windows_console()

		# args = setupArgparse()
		# ports = setupMidi()

		pygame.init()
		pygame.midi.init()


		xt = XTouch()
		xt.connect(1, 6)
		xt.startUpSequence()



if __name__ == '__main__':
	main = Main()
	main.go()