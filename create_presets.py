import json
import argparse




def create_prefix_json(filename: str):
	presets = {'presets': {}}

	presetnum = 1
	for bank in range(100):
		presets['presets'][bank] = {}
		for channel in range(8):
			presets['presets'][bank][channel] = {
				"name": f"preset{presetnum}",
				"encoder": 0,
				"encoder_led": 0,
				"led_bar": 0,
				"button_1": False,
				"button_2": False,
				"button_3": False,
				"button_4": False,
				"fader": 0}

			presetnum += 1
	with open(filename, 'w') as file:
		json.dump(presets, file, indent=4)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output-file')
	args = parser.parse_args()
	create_prefix_json(args.output_file)