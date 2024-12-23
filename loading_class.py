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
from adafruit_display_text import wrap_text_to_pixels #type: ignore

import time
import sys

from collections import namedtuple
from text_handler import TextHandler
from board_parameters import Parameters
from enter_value import UserInput

# Yeah well it crashes now. Going to have to use bitmaps

class ObjLoader:

    def __init__(self, display, ft, i2c, bitmap):

        """ ObjLoader:

                Main class that handles loading all of the functionality of the software. 
                    - display: display object that is used to project an image
                    - ft: the capacitive screen of the display object 
                    - i2c: the i2c object that is used to communicate with the display object
                    - bitmap: the bitmap object that is used to load images

        """

        # Set variables accessible in class
        self._display = display
        self._i2c = i2c
        self._bitmap = bitmap
        self._ft = ft

        # Parameters for the loading screen, items needs to be hardcoded and updated as more things are added
        self._items = 24
        self._load_bar_width = 564
        self.i = 1

        # General parameters of the program
        self._font = bitmap_font.load_font("/src/Arial.bdf")
        self._black = 0x0
        self._white = 0xFFFFFF
        self._gray = 0x888888
        self._green = 0x31D54F

        # The groups used for display
        self._loading_group = None

        # Input Objects
        self.positive_input_obj = None
        self.negative_input_obj = None
        self.delay_input_obj = None
        
        # Output Variables
        self._positive_pulse_val = 0
        self._negative_pulse_val = 0
        self._delay_pulse_val = 0
        self._num_cycles = 0
        self._delay_waveforms = 0
        self._num_waveforms = 0
        self._charge_balance = ""
        self._voltage_val = 0

    # Changes the current view of the display object
    # Currently unused but saved to implement later
    def _view_handler(self, view_name, state):
        view = getattr(self, view_name)
        view.hidden = state

    # Create the loading screen
    def _create_loading_screen(self):

       # Create new group
        self._loading_group = displayio.Group()

        # Make a background color fill
        color_bitmap = displayio.Bitmap(720, 720, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xF8F8F8
        bg_sprite = displayio.TileGrid(color_bitmap,
                                    pixel_shader=color_palette,
                                    x=0, y=0)
        font = bitmap_font.load_font("/src/Arial.bdf")

        # Create progress bar
        pb_background = Rect(78, 360, 564, 90, fill=0xFFFFFF, outline=0x0, stroke=2)
        pb = Rect(78, 360, 47, 90, fill=0x41F0F8, outline=0x0, stroke=2)

        # Create title
        percent_complete = Label(font, text="Loading software . . . ", color=0x0, scale=4)
        percent_complete.x = 78
        percent_complete.y = 240
        
        # Create changing text
        subtext_1 = Label(font, text="Loading main script...", color=0x333333, scale=2)
        subtext_1.x = 78
        subtext_1.y = 468
        subtext_2 = Label(font, text="", color=0x333333, scale=2)
        subtext_2.x = 78
        subtext_2.y = 496

        # Add items to display
        self._loading_group.append(bg_sprite)
        self._loading_group.append(pb_background)
        self._loading_group.append(percent_complete)
        self._loading_group.append(subtext_1)
        self._loading_group.append(subtext_2)
        self._loading_group.append(pb)
        

        #  display the loading group
        self._display.root_group = self._loading_group


    def _update_loading_bar(self):
        
        # Since there is no way to dynamically update a shape, we have to 
        # manually remove it and readd it with an adjusted length. Along
        # with this, as this is not a loop based process, the progress being
        # completed is up to the user to decide. self.i and self._items need
        # to be edited in the init function when more steps are added. 

        # Remove previous shape and add new one with new width
        self._loading_group.pop()
        width = round((564*self.i)/self._items)
        pb = Rect(78, 360, width, 90, fill=0x41F0F8, outline=0x0, stroke=2)
        self._loading_group.append(pb)


    def _update_loading_text(self, log_event):
        
        # Size to provide text wrapping so more information can be included 
        # on the loading screen at time of start. This will be a nice way to log 
        # information later on.
        strings = wrap_text_to_pixels(string=log_event, max_width=282, font=self._font)
        
        # Update strings appropriately
        self._loading_group[3].text = strings[0]
        if len(strings) == 2:
            self._loading_group[4].text = strings[1]
        else:
            self._loading_group[4].text = ""

        time.sleep(0.01) # Give a small amount of time to update

        
        
    # Main Class Method 
    def LoadObjs(self):

        """ LoadObjs:
                - Note: it's not lost on me that this is poor programming practice
                
                Because of the intricacies of CircuitPython not allowing threading, and buttons/labels variables being kept 
                globally after using [del], we cannot create and destroy objects. If we create them in a class, they can be 
                made available by calling a function to grab them and a function to update them, but this is tedious for a 
                first draft. 
                
                As such, everything will be created here, hidden, and made global so the other class methods which act as
                controllers for functionality. The documentation on how displayio and touch_screen treats objects is poor
                at best, but seems to follow methodology similar to CircuitPython. 
        
        """
        
        # Run loading screen
        self._create_loading_screen()
        self._update_loading_text(f"Created the loading screen... ({self.i}/{self._items})")    # These are logging statements for the loading screen
        time.sleep(0.02)

        global view_group
        view_group = displayio.Group()
        
        # Try loading first tab view and all buttons involved
        try: 
            
            #-------------------------------------[VIEW TAB 1]-------------------------------------
            
            # Create group
            global tab_view1_group
            self._update_loading_text(f"Creating tabview group 1 items... ({self.i}/{self._items})")
            tab_view1_group = displayio.Group()
            self.i = self.i + 1                                     # How we itterate a counter to show loading bar progress 
            self._update_loading_bar()                   # Function that handles the progress bar

            # General settings
            self._update_loading_text(f"Setting font/bitmap/color values... ({self.i}/{self._items})")
            font = bitmap_font.load_font("/src/Arial.bdf")
            color_bitmap = displayio.Bitmap(720, 720, 1)
            color_palette = displayio.Palette(1)
            color_palette[0] = 0xF5F5F5
            bg_sprite = displayio.TileGrid(color_bitmap,
                                                pixel_shader=color_palette,
                                                x=0, y=0)
            tab_view1_group.append(bg_sprite)
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Label offsett
            top_margin = 120
            input_box_margin = 16
            space_between_labels = 180
            left_margin = 16


            # Create tab buttons
            global tab1_button
            global tab2_button
            global tab3_button
            global tab_group
            
            tab1_button = Button(x=0, y=0, width=240, height=60, fill_color=self._green, label="Tab 1", label_scale=2, label_font=font)
            tab2_button = Button(x=240, y=0, width=240, height=60, fill_color=self._green, label="Tab 2", label_scale=2, label_font=font)
            tab3_button = Button(x=480, y=0, width=240, height=60, fill_color=self._green, label="Tab 3", label_scale=2, label_font=font)
            
            tab_group = displayio.Group()
            
            tab_group.append(tab1_button)
            tab_group.append(tab2_button)
            tab_group.append(tab3_button)            
            
            
            # Label Creation
            self._update_loading_text(f"Creating positive pulse label... ({self.i}/{self._items})")
            positive_pulse_label = Label(font, text="Positive Pulse Width:", color=0x0, scale=3)
            positive_pulse_label.x = left_margin
            positive_pulse_label.y = top_margin
            self.i = self.i + 1
            self._update_loading_bar()
            

            self._update_loading_text(f"Creating negative pulse label... ({self.i}/{self._items})")
            negative_pulse_label = Label(font, text="Negative Pulse Width", color=0x0, scale=3)
            negative_pulse_label.x = left_margin
            negative_pulse_label.y = top_margin + space_between_labels
            self.i = self.i + 1
            self._update_loading_bar()
            
            self._update_loading_text(f"Creating delay pulse label... ({self.i}/{self._items})")
            delay_pulse_label = Label(font, text="Delay Between Pulses", color=0x0, scale=3)
            delay_pulse_label.x = left_margin
            delay_pulse_label.y = top_margin + space_between_labels*2
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Add Labels to display group
            self._update_loading_text(f"Adding labels to tabview group 1 items... ({self.i}/{self._items})")
            tab_view1_group.append(positive_pulse_label)
            tab_view1_group.append(negative_pulse_label)
            tab_view1_group.append(delay_pulse_label)
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Create an empty bounding box and "button" that functions as a label
            global positive_pulse_input
            global positive_pulse_box
            self._update_loading_text(f"Creating input box for positive pulse... ({self.i}/{self._items})")
            positive_pulse_box = Button(x=left_margin, 
                                        y=top_margin + 40, 
                                        width=620, 
                                        height=90, 
                                        fill_color=0xFFFFFF, 
                                        label="0", 
                                        label_scale=3, 
                                        label_font=font)
            positive_pulse_input = UserInput(display=self._display, touch_screen=self._ft, label_type="positive_pulse")
            self.i = self.i + 1
            self._update_loading_bar()
        

            global negative_pulse_input
            global negative_pulse_box
            self._update_loading_text(f"Creating input box for negative pulse... ({self.i}/{self._items})")
            negative_pulse_box = Button(x=left_margin, 
                                        y=top_margin + 40 + space_between_labels, 
                                        width=620, 
                                        height=90, 
                                        fill_color=0xFFFFFF, 
                                        label="0", 
                                        label_scale=3, 
                                        label_font=font)
            negative_pulse_input = UserInput(display=self._display, touch_screen=self._ft, label_type="negative_pulse")
            self.i = self.i + 1
            self._update_loading_bar()
           
            global delay_pulse_input
            global delay_pulse_box
            self._update_loading_text(f"Creating input box for delay duration... ({self.i}/{self._items})")
            delay_pulse_box = Button(x=left_margin, 
                                    y=top_margin + 40 + space_between_labels*2, 
                                    width=620, 
                                    height=90, 
                                    fill_color=0xFFFFFF, 
                                    label="0", 
                                    label_scale=3, 
                                    label_font=font)
            delay_pulse_input = UserInput(display=self._display, touch_screen=self._ft, label_type="delay_pulse")
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Add to group view
            self._update_loading_text(f"Adding input boxes to tab view 1 group... ({self.i}/{self._items})")
            tab_view1_group.append(positive_pulse_box)
            tab_view1_group.append(negative_pulse_box)
            tab_view1_group.append(delay_pulse_box)
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Create the input objects
            self._update_loading_text(f"Instancing the input box objects for tab view 1... ({self.i}/{self._items})")
            self.positive_input_obj = positive_pulse_input._create_input_object()
            self.negative_input_obj = negative_pulse_input._create_input_object()
            self.delay_input_obj = delay_pulse_input._create_input_object()
            
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Hide items
            tab_view1_group.hidden = True
            self._update_loading_text(f"Finishing tab view 1 group and hiding... ({self.i}/{self._items})")
            self.i = self.i + 1
            self._update_loading_bar()
            
            #-------------------------------------[VIEW TAB 1]-------------------------------------
            
        except RuntimeError:
            pass 
        
        
        
        try:
            #-------------------------------------[VIEW TAB 2]-------------------------------------
            global tab_view2_group
            self._update_loading_text(f"Creating tabview group 2 items... ({self.i}/{self._items})")
            tab_view2_group = displayio.Group()
            self.i = self.i + 1                                     # How we itterate a counter to show loading bar progress 
            self._update_loading_bar()                   # Function that handles the progress bar

            # General settings
            self._update_loading_text(f"Passing background and font/bitmap/color values... ({self.i}/{self._items})")
            bg_sprite = displayio.TileGrid(color_bitmap,
                                                pixel_shader=color_palette,
                                                x=0, y=0)
            tab_view2_group.append(bg_sprite)
            self.i = self.i + 1
            self._update_loading_bar()        
            
            
            # Label Creation
            self._update_loading_text(f"Creating number of cycles label... ({self.i}/{self._items})")
            num_cycles_label = Label(font, text="Number of Cycles:", color=0x0, scale=3)
            num_cycles_label.x = left_margin
            num_cycles_label.y = top_margin
            self.i = self.i + 1
            self._update_loading_bar()
            

            self._update_loading_text(f"Creating delay between waveforms label... ({self.i}/{self._items})")
            wav_del_label = Label(font, text="Delay Between Waveforms", color=0x0, scale=3)
            wav_del_label.x = left_margin
            wav_del_label.y = top_margin + space_between_labels
            self.i = self.i + 1
            self._update_loading_bar()
            
            self._update_loading_text(f"Creating number of waveforms label... ({self.i}/{self._items})")
            num_wav_label = Label(font, text="Number of Waveforms", color=0x0, scale=3)
            num_wav_label.x = left_margin
            num_wav_label.y = top_margin + space_between_labels*2
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Add Labels to display group
            self._update_loading_text(f"Adding labels to tabview group 2 items... ({self.i}/{self._items})")
            tab_view2_group.append(num_cycles_label)
            tab_view2_group.append(wav_del_label)
            tab_view2_group.append(num_wav_label)
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Create an empty bounding box and "button" that functions as a label
            global num_cycles_input
            global num_cycles_box
            self._update_loading_text(f"Creating input box for number of cycles... ({self.i}/{self._items})")
            num_cycles_box = Button(x=left_margin, 
                                        y=top_margin + 40, 
                                        width=620, 
                                        height=90, 
                                        fill_color=0xFFFFFF, 
                                        label="0", 
                                        label_scale=3, 
                                        label_font=font)
            num_cycles_input = UserInput(display=self._display, touch_screen=self._ft, label_type="num_cycles")
            self.i = self.i + 1
            self._update_loading_bar()
        

            global wav_del_input
            global wav_del_box
            self._update_loading_text(f"Creating input box for delay between waveforms... ({self.i}/{self._items})")
            wav_del_box = Button(x=left_margin, 
                                        y=top_margin + 40 + space_between_labels, 
                                        width=620, 
                                        height=90, 
                                        fill_color=0xFFFFFF, 
                                        label="0", 
                                        label_scale=3, 
                                        label_font=font)
            wav_del_input = UserInput(display=self._display, touch_screen=self._ft, label_type="wav_del")
            self.i = self.i + 1
            self._update_loading_bar()
           
            global num_wav_input
            global num_wav_box
            self._update_loading_text(f"Creating input box for total number of waveforms... ({self.i}/{self._items})")
            num_wav_box = Button(x=left_margin, 
                                    y=top_margin + 40 + space_between_labels*2, 
                                    width=620, 
                                    height=90, 
                                    fill_color=0xFFFFFF, 
                                    label="0", 
                                    label_scale=3, 
                                    label_font=font)
            num_wav_input = UserInput(display=self._display, touch_screen=self._ft, label_type="num_wav")
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Add to group view
            self._update_loading_text(f"Adding created input boxes to tab view 2 group... ({self.i}/{self._items})")
            tab_view2_group.append(num_cycles_box)
            tab_view2_group.append(wav_del_box)
            tab_view2_group.append(num_wav_box)
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Create the input objects
            self._update_loading_text(f"Instancing the input box objects for tab view 2... ({self.i}/{self._items})")
            self.num_cyc_input_obj = num_cycles_input._create_input_object()
            self.wav_del_input_obj = wav_del_input._create_input_object()
            self.num_wav_input_obj = num_wav_input._create_input_object()
            
            self.i = self.i + 1
            self._update_loading_bar()
            

            # Hide items
            tab_view2_group.hidden = True
            self._update_loading_text(f"Finishing tab view 2 group and hiding... ({self.i}/{self._items})")
            self.i = self.i + 1
            self._update_loading_bar()
            
            
            #-------------------------------------[VIEW TAB 2]-------------------------------------
        except RuntimeError:
            pass 
        
        
        
        try:
            #-------------------------------------[VIEW TAB 3]-------------------------------------
            global tab_view3_group
            
            #-------------------------------------[VIEW TAB 3]-------------------------------------
        except RuntimeError:
            pass 



    def tab1_controller(self):
        
        # Set variables and display first tab
        ft = self._ft
        display = self._display
        
        view_group.append(tab_view1_group)
        view_group.append(tab_group)
        display.root_group = view_group
        
        view_group.hidden = False
        tab_view1_group.hidden = False
        tab1_button.selected = True
        
        while True:
            
            try:
                for touch in ft.touches:

                    p = (touch["x"], touch["y"])

                    if p is not None:  # Check each slider if the touch point is within the slider touch area
                                
                        if positive_pulse_box.contains(p):

                            # Enter number if box is pressed
                            x = positive_pulse_input.openGUI()
                                    
                            # Update box to display number
                            positive_pulse_box.label = str(x)
                            self._positive_pulse_val = x

                            # update the display root group once more
                            display.root_group = view_group
                                    
                                    
                        elif negative_pulse_box.contains(p):

                            # Enter number if box is pressed
                            x = negative_pulse_input.openGUI()
                                    
                            # Update box to display number
                            negative_pulse_box.label = str(x)
                            self._negative_pulse_val = x

                            # update the display root group once more
                            display.root_group = view_group
                                    
                                    
                        elif delay_pulse_box.contains(p):

                            # Enter number if box is pressed
                            x =delay_pulse_input.openGUI()
                                    
                            # Update box to display number
                            delay_pulse_box.label = str(x)
                            self._delay_pulse_val = x
                            
                            # update the display root group once more
                            display.root_group = view_group
                        
                        
                        elif tab2_button.contains(p):
                            
                            # Change to tab 2
                            tab1_button.selected = False
                            tab_view1_group.hidden = True
                            
                            view_group.pop()
                            view_group.pop()
                            
                            time.sleep(0.02)
                            return self.tab2_controller()
                        
                        # elif tab3_button.contains(p)
                        
                        # elif start.contains(p)
                        
                        
                        time.sleep(0.02)
                                    
            except RuntimeError:
                pass

    
    def tab2_controller(self):
        
        # Set variables and display second tab
        view_group.append(tab_view2_group)
        view_group.append(tab_group)
                
        tab2_button.selected = True
        ft = self._ft
        display = self._display
        display.root_group = view_group
        
        tab_view2_group.hidden = False
        
        while True:
            
            try:
                for touch in ft.touches:

                    p = (touch["x"], touch["y"])

                    if p is not None:  # Check each slider if the touch point is within the slider touch area
                                
                        if num_cycles_box.contains(p):

                            # Enter number if box is pressed
                            x = num_cycles_input.openGUI()
                                    
                            # Update box to display number
                            num_cycles_box.label = str(x)
                            self._num_cycles = x

                            # update the display root group once more
                            display.root_group = view_group
                                    
                                    
                        elif wav_del_box.contains(p):

                            # Enter number if box is pressed
                            x = wav_del_input.openGUI()
                                    
                            # Update box to display number
                            wav_del_box.label = str(x)
                            self._delay_waveforms = x

                            # update the display root group once more
                            display.root_group = view_group
                                    
                                    
                        elif num_wav_box.contains(p):

                            # Enter number if box is pressed
                            x =num_wav_input.openGUI()
                                    
                            # Update box to display number
                            num_wav_box.label = str(x)
                            self._num_waveforms = x
                            
                            # update the display root group once more
                            display.root_group = view_group
                        
                        
                        elif tab1_button.contains(p):
                            
                            # Change to tab 2
                            tab2_button.selected = False
                            tab_view2_group.hidden = True
                            
                            view_group.pop()
                            view_group.pop()
                            
                            time.sleep(0.02)
                            return self.tab1_controller()
                        
                        # elif tab3_button.contains(p)
                        
                        # elif start.contains(p)
                        
                        
                        time.sleep(0.02)
                                    
            except RuntimeError:
                pass
    

    
    # def tab2_controller(self):
    
    # def tab3_controller(self):
    