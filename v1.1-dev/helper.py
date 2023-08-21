# FUNCTIONS

def centerString(string: str, length: int = 7) -> str:
    if len(string) >= length:
        return string[:length]
    else:
        left_padding = (length - len(string)) // 2
        right_padding = length - len(string) - left_padding
        return ' ' * left_padding + string + ' ' * right_padding


# CONSTANTS

# map buttons to specific functions
# arguments are also suported, add them as extra values to the tuple
# as example, map button 92 to "updateBank(1)"
# 92: ('updateBank', 1)
BUTTONS = {
    92: ('updateBank', 1),
    93: ('updateBank', -1),
    94: ('updateMode', 'channel'),
    95: ('updateMode', 'presets'),
    96: ('pressKey', 'up'),
    97: ('pressKey', 'down'),
    98: ('pressKey', 'left'),
    99: ('pressKey', 'right')
}


# used midi message types
MIDITYPES = {
			'note_on': 0x90,
			'note_off': 0x80,
			'control_change': 0xb0}

# backlight colors
COLORS = {
		'off'	 : 0b000,
		'black'	 : 0b000,
		'red'	 : 0b001,	
		'green'	 : 0b010,
		'yellow' : 0b011,
		'blue'	 : 0b100,
		'magenta': 0b101,
		'cyan'	 : 0b110,
		'white'	 : 0b111}

# 7-segment display chars
#          GFEDCBA
SEGMENTS = {
    '0': 0b0111111,
    '1': 0b0000110,
    '2': 0b1011011,
    '3': 0b1001111,
    '4': 0b1100110,
    '5': 0b1101101,
    '6': 0b1111101,
    '7': 0b0000111,
    '8': 0b1111111,
    '9': 0b1101111,
    'a': 0b1110111,
    'b': 0b1111100,
    'c': 0b0111001,
    'd': 0b1011110,
    'e': 0b1111001,
    'f': 0b1110001,
    'g': 0b0111101,
    'h': 0b1110100,
    'i': 0b0000100,
    'j': 0b0011110,
    'l': 0b0111000,
    'n': 0b0110111,
    'o': 0b1011100,
    'p': 0b1110011,
    'q': 0b1100111,
    'r': 0b1010000,
    's': 0b1101101,
    't': 0b1111000,
    'u': 0b0011100,
    'x': 0b1110110,
    'y': 0b1101110,
    '-': 0b1000000,
    ' ': 0b0000000
}

# The below are not possible:
# k, m, v, w, z
# Some are possible but are the same as others:
# Like v, it is the same as u.
# And z, it is the same as 2.
# The letters k, m and w are just not possible with a 7 segment display.
# If you know a better "font" or can inplement more letters and keep everyting readable please create a github issue or pull request. 