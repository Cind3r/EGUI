import displayio #type: ignore
import terminalio #type: ignore
import busio #type: ignore
import board #type: ignore
import dotclockframebuffer #type: ignore
from framebufferio import FramebufferDisplay #type: ignore
import adafruit_focaltouch #type: ignore
from adafruit_button import Button #type: ignore
from adafruit_display_text.label import Label #type: ignore
from adafruit_bitmap_font import bitmap_font #type: ignore
from adafruit_display_shapes.rect import Rect #type: ignore
from slider import Slider

import random 
import time

# Custom Classes/Functions
from collections import namedtuple
from text_handler import TextHandler
from board_parameters import Parameters
from enter_value import UserInput
from loading_class import ObjLoader #type: ignore

# NEED
# Set default values and keep groups unloaded unless otherwise changed
# Don't unload any changes made as well

# NOTE: the pickle module could potentially be used to save each window as a object file and 
#             load/unload it. I don't know if this would be faster, but it would prevent potential 
#             issues with deleting classes and allow for a object containing parameters to be
#             dumped and passed to the second micro controller. 

# TODO: Make this a class that can be called when a text box is pressed on,
# TODO: Pass input into the class (default values for treatment) by making the display text variable
# TODO: Loading these buttons is honestly pretty slow, their position should likely be hard coded 
#             later on (as I haven't messed around with any of the display settings other than screen
#             size and resolution)
# TODO: Add a touch response under main loop that will bring up the terminal in the event of failure
# TODO: Add a touch response under main loop that will reset the application

#----------------------------[PROGRAM START]-----------------------------

# Necessary for instancing display
displayio.release_displays()

# Instance display
display_obj = Parameters()
display_obj.load_board()

# Save necessary variables
bitmap = display_obj.get_board_val("bitmap") # base bitmap settings are set here, these can change 
display = display_obj.get_board_val("display")
i2c = display_obj.get_board_val("i2c")

# Dump object to free up memory
del display_obj

# Create capacitive touch object
display.auto_refresh = True
ft = adafruit_focaltouch.Adafruit_FocalTouch(i2c, address=0x48)

egui = ObjLoader(display, ft, i2c, bitmap)
egui.LoadObjs()

#display.root_group = getattr(egui,'tab_view1_group')
#egui._view_handler('tab_view1_group', False)



# Main loop
while True:
    
    try:
        
        egui.tab1_controller()

                   
    except RuntimeError:
           pass