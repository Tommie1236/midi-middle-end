import json
import argparse




def create_prefix_json(filename: str):
	presets = {'presets': {}}

	presetnum = 1
	for bank in range(100):
		presets['presets'][f"bank_{bank}"] = {}
		for channel in range(8):
			presets['presets'][f"bank_{bank}"][f"channel_{channel}"] = {
				"name": f"preset{presetnum}",
				"color": "white",
				"encoder": {"value": 0},
				"encoder_led": {"value": 0},
				"led_bar": {"value": 0},
				"button_1": {"value": False},
				"button_2": {"value": False},
				"button_3": {"value": False},
				"button_4": {"value": False},
				"fader": {"value": 0}}

			presetnum += 1
	with open(filename, 'w') as file:
		json.dump(presets, file, indent=4)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output-file')
	args = parser.parse_args()
	create_prefix_json(args.output_file)