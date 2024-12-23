import board # type: ignore
import dotclockframebuffer #type: ignore
from framebufferio import FramebufferDisplay #type: ignore
import displayio #type: ignore
import busio #type: ignore
import time
from adafruit_bitmap_font import bitmap_font #type: ignore
from adafruit_button import Button #type: ignore
from adafruit_display_shapes.rect import Rect #type: ignore
from adafruit_display_text.label import Label #type: ignore
import adafruit_focaltouch #type: ignore




from collections import namedtuple
from text_handler import TextHandler
from board_parameters import Parameters

# NEED
# Set default values and keep groups unloaded unless otherwise changed
# Don't unload any changes made as well

# TODO: Make this a class that can be called when a text box is pressed on,
# TODO: Pass input into the class (default values for treatment) by making the display text variable
# TODO: Loading these buttons is honestly pretty slow, their position should likely be hard coded 
#             later on (as I haven't messed around with any of the display settings other than screen
#             size and resolution)
# TODO: If the display is called more than once in a loop it will error out as the group already exists. 
#             This means the display object created by this class will need to be destroyed after its use. 

class UserInput:

    def __init__(self, display, touch_screen, label_type=""):

        self._display = display
        self._ft = touch_screen
        self._font_location = "/src/Arial.bdf" # Path to font file (.bdf)
        
        # --| Button Config |-------------------------------------------------
        self._button_width = 180
        self._button_height = 90
        self._button_margin = 8
        self._button_text_scale = 2
        self._label_offset = 620
        self._max_digits = 29
        self._black = 0x0
        self._white = 0xFFFFFF
        self._gray = 0x888888
        self._buttons = []
        # --| Button Config |-------------------------------------------------

        self._default_label_number = 0
        self._label_type = label_type
        self._font = None
        self._display_text = None
        self.input_group = displayio.Group()

    # Create Coordinate Grid for equally spaced buttons
    # This likely should be changed to be static to improve speed
    def _button_grid(self, row, col):

        """ Use this to change the [x] and [y] offsets of the input buttons respectively"""

        x_offset = 70 # same math as below
        y_offset = 198 # 5 rows @ 90 px each and 8 px margin comes out to 720 - 490 (however it starts margin from the top so add 8-16 on preference)
        Coords = namedtuple("Point", "x y")

        return Coords(self._button_margin * (row + 1) + self._button_width * row + x_offset,
                                self._button_margin * (col + 1) + self._button_height * col + y_offset)

    # Dynamically creates the buttons
    def _add_button(self, row, col, label, width=1):
        pos = self._button_grid(row, col)
        font = self._get_font()
        new_button = Button(
                            x=pos.x, 
                            y=pos.y,
                            width=self._button_width * width + self._button_margin * (width - 1),
                            height=self._button_height, 
                            label=label, 
                            label_font=font,
                            label_color=self._black, 
                            fill_color=self._white, 
                            style=Button.ROUNDRECT,
                            label_scale=self._button_text_scale
                            )
        
        self._buttons.append(new_button)
        return new_button


    def _find_button(self, label):
        result = None
        for _, btn in enumerate(self._buttons):
            if btn.label == label:
                result = btn
        return result


    # Method to set unconvential board parameters
    def _get_font(self):
        return bitmap_font.load_font(self._font_location)
            

    # This is where the entered number will appear
    def _create_input_object(self):

        # Make the display context
        font = self._get_font()

        # Make a background color fill
        color_bitmap = displayio.Bitmap(720, 720, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = self._gray
        bg_sprite = displayio.TileGrid(color_bitmap,
                                    pixel_shader=color_palette,
                                    x=0, y=0)
        self.input_group.append(bg_sprite)

        # Create display bar for numbers entered (manually sized for the 720x720 screen)
        border = Rect(78, 32, 564, 90, fill=self._white, outline=self._black, stroke=2)
        calc_display = Label(font, text="0", color=self._black, scale=4)
        calc_display.y = 88
        calc_display.x = 90

        # Create input buttons from top -> bottom (x,y origin starts at the top left of the screen)
        clear_button = self._add_button(0, 0, "Clear")
        self._add_button(2, 0, "Done")

        self._add_button(0, 1, "7")
        self._add_button(1, 1, "8")
        self._add_button(2, 1, "9")

        self._add_button(0, 2, "4")
        self._add_button(1, 2, "5")
        self._add_button(2, 2, "6")

        self._add_button(0, 3, "1")
        self._add_button(1, 3, "2")
        self._add_button(2, 3, "3")

        self._add_button(0, 4, "0", 2)
        self._add_button(2, 4, ".")

        # add buttons to the display group
        self.input_group.append(border)
        self.input_group.append(calc_display)
        for b in self._buttons:
            self.input_group.append(b)

        self._display_text = TextHandler(calc_display, clear_button, self._label_offset)


    # Begin input loop
    def openGUI(self):
        
        self.input_group.hidden = False

        ft = self._ft
        button = ""
        self._display.root_group = self.input_group

        # wait momentarily to not pick up false input
        time.sleep(0.05)

        # main loop
        while True:
                try:
                    
                    for touch in ft.touches:

                        point = (touch["x"], touch["y"])

                        if point is not None:
                            
                            # Button Down Events
                            for _, b in enumerate(self._buttons):
                            
                                if b.contains(point) and button == "":
                                    b.selected = True
                                    button = b.label
                                    time.sleep(0.1) # Sleep necessary for button animation and accidental overflow

                                # Perform button up and save value to display and variable 
                                elif button == "Done":
                                    # Return value and close group 
                                    self._default_label_number = self._display_text._get_text()
                                    b = self._find_button(button)
                                    if b is not None:
                                            b.selected = False
                                    button = ""
                                    self.input_group.hidden = True
                                    return self._display_text._get_text()
                                
                                elif button != "":
                                    # Button Up Events
                                    # The loop will execute again before you can lift your finger, we assume as such
                                    # and set the update to catch this rather than increasing the sleep time which
                                    # feels bad for user experience and also allows you to hold down a button to insert
                                    # multiple characters. Neat work around if I say so. 
                                    self._display_text.add_input(button)
                                    b = self._find_button(button)
                                    if b is not None:
                                            b.selected = False
                                    button = ""
                                
                                

                            time.sleep(0.05)
                    
                except RuntimeError:
                    pass
            

    
    #---------[EXTRANEOUS METHODS]------------------------------
    def calculate(number_one):
        result = eval(number_one)
        if int(result) == result:
            result = int(result)
        return str(result)
    

    def _get_text(self,var):
        return getattr(self, var)
    
    def __del__(self):
        # Class deconstructor for group handling 
        return
    
    #---------[EXTRANEOUS METHODS]------------------------------
    


