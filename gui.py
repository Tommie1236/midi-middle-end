# Design can be found on main repo.
# This GUI is made by xxx
# Written by xxx
# Code_ver = xxx

print("[GUI] starting...")
import customtkinter as ctk
import tkinter as tk
from tkinter import *

ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class fixed_values:
    def __init__(fixed):
        fixed.version = "0.1.0 - beta 1.0"
        fixed.credits = "Gui written by Timo Oosterom and Niek van Reenen"

class main(ctk.CTk):
	def __init__(self):
		super().__init__()

		container = ctk.CTkFrame(self)
		container.pack(side='top', fill="both", expand = True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)
        
		self.frames = {}
		self.basic_screen = basic_screen
		self.help_page = help_page
		self.bank_selector = bankselector
        # add more screens here

		for F in {basic_screen, help_page, bankselector}: # add also the screens here
			frame = F(self, container)
			self.frames[F] = frame #select the screen to be called
			frame.grid(row=0, column=0, sticky="nsew")

		print(fixed_values().credits)
		print(f"version loaded: {fixed_values().version}")
		print('[GUI] succesfully started')
		self.framecall(basic_screen)    

	def framecall(self, cnt):
		frame = self.frames[cnt]
		menubar = frame.menubar(self)
		self.configure(menu=menubar)
		frame.tkraise()



class basic_screen(ctk.CTkFrame):
	def __init__(self, master, container):
		self.mdvar1 = 0
		self.mdvar2 = 0
		self.cmode = 'No mode selected'
		super().__init__(container)



		## DO NOT CHANGE ANY OF THESE VALUES!
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)
		self.rowconfigure(2, weight=1)
		self.rowconfigure(3, weight=1)
		self.rowconfigure(4, weight=1)
		self.rowconfigure(5, weight=1)
		self.rowconfigure(6, weight=1)
		self.rowconfigure(7, weight=1) 
		self.rowconfigure(8, weight=10)	# do not use!

		self.columnconfigure(0, weight=1) # do not use!
		self.columnconfigure(1, weight=1)
		self.columnconfigure(2, weight=1) # center
		self.columnconfigure(3, weight=1)
		self.columnconfigure(4, weight=1) # do not use!
		

		## LABELS
		label = ctk.CTkLabel(self, text='MIDIATOR', font=('Calibri', 20, 'bold'))
		label.grid(row=0,column=2,sticky='n', pady=10)
		
		mode_label = ctk.CTkLabel(self, text="MODE:", font=('Calibri', 20, 'bold'))
		mode_label.grid(row=1, column=1)	

		signal_label = ctk.CTkLabel(self, text="LAST-KNOW SIGNALS:", font=('Calibri', 12, 'bold'))
		signal_label.grid(row=5, column=1)

		signal_label = ctk.CTkLabel(self, text=str(self.mdvar2), font=('Calibri', 12)) # code to change not written yet
		signal_label.grid(row=7, column=2)

		signal_label = ctk.CTkLabel(self, text="MIDI_IN:", font=('Calibri', 12))
		signal_label.grid(row=6, column=1)

		signal_label = ctk.CTkLabel(self, text="MIDI_OUT:", font=('Calibri', 12))
		signal_label.grid(row=7, column=1)

		signal_label = ctk.CTkLabel(self, text=str(self.mdvar1), font=('Calibri', 12)) # code to change not written yet
		signal_label.grid(row=6, column=2)

		signal_label = ctk.CTkLabel(self, text=str(self.mdvar2), font=('Calibri', 12)) # code to change not written yet
		signal_label.grid(row=7, column=2)

		currmd_label = ctk.CTkLabel(self, text='CURRENT:', font=('Calibri', 20, 'bold')) # code to change not written yet
		currmd_label.grid(row=1, column=2)

		currmd_disp_label = ctk.CTkLabel(self, text=str(self.cmode), font=('Calibri', 12,)) # code to change not written yet
		currmd_disp_label.grid(row=2, column=2)

		bnk_label = ctk.CTkLabel(self, text='MENU:', font=('Calibri', 20, 'bold')) # code to change not written yet
		bnk_label.grid(row=1, column=3)

		cred_label = ctk.CTkLabel(self, text=str(fixed_values().credits), font=('Calibri', 8))
		cred_label.grid(row=10,column=2,sticky='s')

		## BUTTONS
		preset_bttn = ctk.CTkButton(self, text="PRESETS", font=('Calibri', 10, 'bold'), command=self.preset_btn, width=100, height=25, border_width=0, corner_radius=180)
		preset_bttn.grid(column=1, row=2)

		chnl_bttn = ctk.CTkButton(self, text="CHANNELS", font=('Calibri', 10, 'bold'), command=self.chnl_btn, width=100, height=25, border_width=0, corner_radius=180)
		chnl_bttn.grid(column=1, row=3)

		bank_bttn = ctk.CTkButton(self, text="BANK", font=('Calibri', 10, 'bold'), command=lambda: master.framecall(master.bank_selector), width=100, height=25, border_width=0, corner_radius=180)
		bank_bttn.grid(row=2, column=3)


	def preset_btn(self):
		self.cmode = 'PRESETS'
		self.reprint()
	
	def chnl_btn(self):
		self.cmode = 'CHANNELS'
		self.reprint()

	def bank_btn(self):
		pass	

	def reprint(self):
		# NOT INITIAL, ONLY IF VALUE CHANGES
		signal_label = ctk.CTkLabel(self, text=str(self.mdvar1), font=('Calibri', 12)) # code to change not written yet
		signal_label.grid(row=6, column=2)

		signal_label = ctk.CTkLabel(self, text=str(self.mdvar2), font=('Calibri', 12)) # code to change not written yet
		signal_label.grid(row=7, column=2)

		currmd_disp_label = ctk.CTkLabel(self, text=str(self.cmode), font=('Calibri', 18,)) # code to change not written yet
		currmd_disp_label.grid(row=2, column=2, ipadx=25)
		

	def cngtemp(self):
		print("update succesfull")
		self.mdvar1 += 1
		self.mdvar2 += 5
		self.reprint()
		

	def tempcmd(self):
		print("RR1 - BTN NOT IN USE")	

	def menubar(self, master):
		menubar = Menu(master, bd=3, relief=RAISED, activebackground="#90cded")

		filemenu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")
		menubar.add_cascade(label="Setup", menu=filemenu)
		filemenu.add_command(label="Home Page", command=lambda: master.framecall(master.basic_screen))

		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=master.quit)  

		help_menu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")
		menubar.add_cascade(label="Help", menu=help_menu)
		help_menu.add_command(label="Help window", command=lambda: master.framecall(master.help_page))

		return menubar

class help_page(ctk.CTkFrame):
	def __init__(self, master, container):
		super().__init__(container)
		
		label = ctk.CTkLabel(self, text=str(f'Help menu'), font=('Calibri', 40, 'bold'))
		label.pack(padx=0,pady=0)

		version_label = ctk.CTkLabel(self, text=fixed_values().credits, font=('Calibri', 10))
		version_label.pack(padx=0,pady=0,side=BOTTOM)

		credits_label = ctk.CTkLabel(self, text=str(f'version: {fixed_values().version}'), font=('Calibri', 10))
		credits_label.pack(padx=0,pady=0,side=BOTTOM)

	
	
	def menubar(self, master):
		menubar = Menu(master, bd=3, relief=RAISED, activebackground="#90cded")

		filemenu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")
		menubar.add_cascade(label="Setup", menu=filemenu)
		filemenu.add_command(label="Home Page", command=lambda: master.framecall(master.basic_screen))

		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=master.quit)  

		help_menu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")
		menubar.add_cascade(label="Help", menu=help_menu)
		help_menu.add_command(label="Help window", command=lambda: master.framecall(master.help_page))

		return menubar

class bankselector(ctk.CTkFrame):
	def __init__(self, master, container):
		super().__init__(container)

		# LABELS
		bank_lbl = ctk.CTkLabel(self, text='BANK SELECTOR', font=('Calibri', 20, 'bold'))
		bank_lbl.place(relx=0.5,  rely=0.05,  anchor=N)


		# SERIE 1
		btn1_1 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_1.place(x=80, y=100)

		btn1_2 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_2.place(x=50, y=130)

		btn1_3 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_3.place(x=110, y=130)

		btn1_4 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_4.place(x=80, y=160)

		btn1_5 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_5.place(x=50, y=190)

		btn1_6 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_6.place(x=110, y=190)

		btn1_7 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn1_7.place(x=80, y=220)

		# SERIE 2
		btn2_1 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_1.place(x=200, y=100)

		btn2_2 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_2.place(x=170, y=130)

		btn2_3 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_3.place(x=230, y=130)

		btn2_4 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_4.place(x=200, y=160)

		btn2_5 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_5.place(x=170, y=190)

		btn2_6 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_6.place(x=230, y=190)

		btn2_7 = ctk.CTkButton(self, text="", width=25, height=10, border_width=0, corner_radius=180)
		btn2_7.place(x=200, y=220)

		# BUTTONS
		btn_bankdwn = ctk.CTkButton(self, text="DOWN", font=('Calibri', 20, 'bold'), width=100, height=25, border_width=0, corner_radius=180)
		btn_bankdwn.place(x=280, y=180)

		btn_bankup = ctk.CTkButton(self, text="UP", font=('Calibri', 20, 'bold'), width=100, height=25, border_width=0, corner_radius=180)
		btn_bankup.place(x=280, y=120)

		btn_back = ctk.CTkButton(self, text="BACK", font=('Calibri', 20, 'bold'), command=lambda: master.framecall(master.basic_screen), width=100, height=25, border_width=0, corner_radius=180)
		btn_back.place(x=150, y=350)


	def menubar(self, master):
			menubar = Menu(master, bd=3, relief=RAISED, activebackground="#90cded")
			filemenu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")

			menubar.add_cascade(label="Setup", menu=filemenu)
			filemenu.add_command(label="Home Page", command=lambda: master.framecall(master.basic_screen))

			filemenu.add_separator()
			filemenu.add_command(label="Exit", command=master.quit)  

			help_menu = Menu(menubar, tearoff=0, relief=RAISED, activebackground="#90cded")
			menubar.add_cascade(label="Help", menu=help_menu)
			help_menu.add_command(label="Help window", command=lambda: master.framecall(master.help_page))

			return menubar



def startup():
	startup = main()
	startup.wm_title("midiator")
	startup.geometry("400x400")
	startup.resizable(False, False)
	startup.iconphoto(False, tk.PhotoImage(file="gui_assets/mdlogo.png")) 
	startup.mainloop() 

def bootstrap():
	pass	

if __name__ == '__main__':
    startup()
        
       