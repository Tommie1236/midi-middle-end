import pygame.midi
import time

def send_midi_messages():
    pygame.midi.init()

    # Get the available MIDI devices
    device_count = pygame.midi.get_count()
    if device_count == 0:
        print("No MIDI devices found.")
        return

    print("Available MIDI devices:")
    for i in range(device_count):
        device_info = pygame.midi.get_device_info(i)
        device_name = device_info[1].decode("utf-8")
        print("[{}] {}".format(i, device_name))

    # Prompt user to choose a MIDI device
    while True:
        try:
            device_index = int(input("Enter the index of the MIDI device you want to use: "))
            if 0 <= device_index < device_count:
                break
            else:
                print("Invalid device index. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid device index.")

    midi_output = pygame.midi.Output(device_index)

    print("Sending MIDI messages.")

    try:
        # Control the 7-segment displays
        segment_data = [
            0b0111111,  # 0
            0b0000110,  # 1
            0b1011011,  # 2
            0b1001111,  # 3
            0b1100110,  # 4
            0b1101101,  # 5
            0b1111101,  # 6
            0b0000111,  # 7
            0b1111111,  # 8
            0b1101111,  # 9
            0b1110111,  # A
            0b1111100   # B
        ]

        # Dots for displays 1 to 7 (7-bit value)
        dots_displays_1_7 = 0b0101010

        # Dots for displays 8 to 12 (5-bit value)
        dots_displays_8_12 = 0b00000

        # Construct the SysEx message for segment displays
        sysex_message_segment_displays = [0xF0, 0x00, 0x20, 0x32, 0x14, 0x37]
        sysex_message_segment_displays.extend(segment_data)
        sysex_message_segment_displays.extend([dots_displays_1_7, dots_displays_8_12])
        sysex_message_segment_displays.extend([0xF7])

        # Send the SysEx message for segment displays
        midi_output.write_sys_ex(pygame.midi.time(), sysex_message_segment_displays)
        print("SysEx message sent for segment displays.")

        # Send note values from 0 to 103
        for note in range(104):
            midi_output.note_on(note, velocity=127)
            time.sleep(0.1)
            midi_output.note_off(note)

            # Alternate the dots for display 1 to 7
            dots_displays_1_7 = ~dots_displays_1_7 & 0b1111111
            sysex_message_segment_displays[-2] = dots_displays_1_7

            # Alternate the dots for display 8 to 12
            dots_displays_8_12 = ~dots_displays_8_12 & 0b11111
            sysex_message_segment_displays[-1] = dots_displays_8_12

            # Send the updated SysEx message for segment displays
            print(midi_output)
            midi_output.write_sys_ex(pygame.midi.time(), sysex_message_segment_displays)
            time.sleep(0.1)

    finally:
        # Clean up MIDI resources
        del midi_output
        pygame.midi.quit()

if __name__ == "__main__":
    print('Dont use this version!')
    
    send_midi_messages()
