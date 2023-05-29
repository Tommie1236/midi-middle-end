# midi-middle-end

#### a little program in between the `behringer x-touch daw` and the `mydmx 3.0` software for additional functionality.

to install all the required packages, run this (in a venv).  
`pip3 install -r requirements.txt`

uses loopmidi to create a virtual hardware midi port so python and mydmx can talk to eachother


## Goal:  
  
Be able to expand a midi controller's input to a lot more.

### 7 segment displays:  

0,1 = bank nr.  
2-11 = either `presets` or `channels`.

### Lcd scribble strips:
Name of preset or channel number.

### Fader bank `<`, `>`buttons:
Change the current bank and display that to 7 segment 0,1

### Channel `<`, `>`buttons:  
Change the current mode:  
`<`: to presets mode.  
`>`: to channels mode.  




<br>  
<br>  
<br>  
<br>
contact tommie1236 (timo) for more info.
