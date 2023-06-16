import json
from dotwiz import DotWiz

# Load JSON data into a DotWiz object
with open('empty-presets.json', 'r') as file:
    json_data = DotWiz(json.load(file))

# Access nested data using dot notation
print(json_data.presets.bank0)  # Output: v
print(json_data.presets.bank1)  # Output: 5
print(f'{json_data.presets.bank0.channel0}')  # Output: 3.21



# Convert DotWiz object back to a Python dictionary
data_dict = json_data.to_dict()

# Save the modified data as JSON
with open('modified_data.json', 'w') as file:
    json.dump(data_dict, file)