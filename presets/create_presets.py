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
				"encoder": {"channel": 0, "value": 0},
				"encoder_led": {"channel": 0, "value": 0},
				"led_bar": {"channel": 0, "value": 0},
				"button_1": {"channel": 0, "value": False},
				"button_2": {"channel": 0, "value": False},
				"button_3": {"channel": 0, "value": False},
				"button_4": {"channel": 0, "value": False},
				"fader": {"channel": 0, "value": 0}}

			presetnum += 1
	with open(filename, 'w') as file:
		json.dump(presets, file, indent=4)



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output-file')
	args = parser.parse_args()
	create_prefix_json(args.output_file)