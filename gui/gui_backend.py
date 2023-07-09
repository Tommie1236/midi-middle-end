# Niek van Reenen & Timo Oosterom 2023

class msg:
    def __init__(msg):
        msg.msg_pt1 = '[GUI_BACKEND] SUCCESFULLY LOADED'
        msg.msg_bno = '[GUI_BACKEND] BUTTON NOT OCCUPIED'

class bankbuttons_backend:
	def btn1_1():
		print(msg().msg_bno)
	def btn1_2():
		print(msg().msg_bno)
	def btn1_3():
		print(msg().msg_bno)
	def btn1_4():
		print(msg().msg_bno)
	def btn1_5():
		print(msg().msg_bno)
	def btn1_6():
		print(msg().msg_bno)
	def btn1_7():
		print(msg().msg_bno)

    ## S2
	def btn2_1():
		print(msg().msg_bno)
	def btn2_2():
		print(msg().msg_bno)
	def btn2_3():
		print(msg().msg_bno)	
	def btn2_4():
		print(msg().msg_bno)
	def btn2_5():
		print(msg().msg_bno)
	def btn2_6():
		print(msg().msg_bno)
	def btn2_7():
		print(msg().msg_bno)
    
	## Bank Control Buttons
	def btn_up():
		print(msg().msg_bno)
	def btn_dwn():
		print(msg().msg_bno)
    
class modeint:
	
	def mode_channels():
		print(msg().msg_bno)
		## exec here

	def mode_presets():
		print(msg().msg_bno)
		## exec here

class signals:
	def __init__(sgnl):
		sgnl.lastknown_out = "0"
		sgnl.lastknown_in = "0"
		sgnl.past_out = []
		sgnl.past_in = []

	def confignew(sgnl):
		sgnl.past_out.append(sgnl.lastknown_out)
		sgnl.past_in.append(sgnl.lastknown_in)
		sgnl.lastknown_out = "TEMP"
		sgnl.lastknown_in = "TEMP"


'''
class signal_refresh:
	def confignew():
		lastknown_out = signals().lastknown_out
		lastknown_in = signals().lastknown_in
		past_out = signals().past_out
		past_in = signals().past_in
		past_out.append(lastknown_out)
		past_in.append(lastknown_in)
		lastknown_in = "SUCCES" # adaption here
		lastknown_out = "SUCCES" # adaption here
		signals().past_in = past_in
		signals().past_out = past_out
'''