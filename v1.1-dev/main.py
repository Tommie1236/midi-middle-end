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
		return self.debounce(data) 

	def debounce(lst) -> list:
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
		self.leds = [0 for _ in range(94)]

		self.encoders = [0 for _ in range(8)]

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
		self.stripsTop, self.stripsBottom = [0x00 for _ in range(8)]
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
	
	# 




class Main():
	def go():
		if platform.system() == 'Windows':
			from colorama import just_fix_windows_console
			just_fix_windows_console()



if __name__ == '__main__':
	Main.go()