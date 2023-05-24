import rtmidi

# Get the available MIDI input ports
midi_in = rtmidi.MidiIn()
available_ports = midi_in.get_ports()

# Display the available MIDI input ports
print("Available MIDI input ports:")
for i, port_name in enumerate(available_ports):
    print(f"{i+1}. {port_name}")

# Prompt the user to choose a MIDI input port
input_port_index = int(input("Choose a MIDI input port: ")) - 1
if input_port_index < 0 or input_port_index >= len(available_ports):
    print("Invalid input port index!")
    exit()

# Open the chosen MIDI input port
midi_in.open_port(input_port_index)

# Get the available MIDI output ports
midi_out = rtmidi.MidiOut()
available_ports = midi_out.get_ports()

# Display the available MIDI output ports
print("Available MIDI output ports:")
for i, port_name in enumerate(available_ports):
    print(f"{i+1}. {port_name}")

# Prompt the user to choose a MIDI output port
output_port_index = int(input("Choose a MIDI output port: ")) - 1
if output_port_index < 0 or output_port_index >= len(available_ports):
    print("Invalid output port index!")
    exit()

# Open the chosen MIDI output port
midi_out.open_port(output_port_index)

# MIDI input callback function
def midi_input_callback(message, time_stamp):
    print(f"MIDI received: {message} at time {time_stamp}")
    # Process the received MIDI message as desired

# Set the callback function for MIDI input
midi_in.set_callback(midi_input_callback)

# Send MIDI messages to the chosen MIDI output port
message = [0x90, 60, 100]  # Example MIDI note on message
midi_out.send_message(message)

# Keep the program running until interrupted
while True:
    pass

# Cleanup
midi_in.close_port()
midi_out.close_port()
