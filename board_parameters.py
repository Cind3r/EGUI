import board # type: ignore
import dotclockframebuffer #type: ignore
from framebufferio import FramebufferDisplay #type: ignore
import displayio #type: ignore
import busio #type: ignore

class Parameters:

    """ This is a holding spot for the parameters for the screen being used 
            with the Adafruit Qualia ESP32-S3. The screen being used for 
            this project is the RGB-666 720x720 capacitive touch screen. 
            As such, much of the set up for this class will revolve around these
            parameters, however, it can be edited as necessary to fit others. """
    
    # NOTE: "import baord" and displayio.release_displays() must be called before instancing this class
    #               otherwise this function will fail. This is just a neat and compact method of storing the 
    #               info of the board being used. 

    def __init__(self, screen_width=720, screen_height=720, capacitive_touch=True, board=board):
        
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._capacitive_touch = capacitive_touch

        # Initialize the Display
        self._tft_pins = dict(board.TFT_PINS)
        self._tft_timings = {
            "frequency": 16000000,
            "width": screen_width,
            "height": screen_height,
            "hsync_pulse_width": 2,
            "hsync_front_porch": 46,
            "hsync_back_porch": 44,
            "vsync_pulse_width": 2,
            "vsync_front_porch": 16,
            "vsync_back_porch": 18,
            "hsync_idle_low": False,
            "vsync_idle_low": False,
            "de_idle_high": False,
            "pclk_active_high": False,
            "pclk_idle_high": False,
        }

    # Method to update values beyond isntancing the board
    def _set_val(self, var, val):
        if hasattr(self, var):  # Check if the variable exists
            setattr(self, var, val)  # Dynamically update the variable
        else:
            raise AttributeError(f"ERROR: '{type(self).__name__}' has no attribute '{var}'")
        
    # Method to set unconvential board parameters
    def __setattr__(self, var, val):
        if hasattr(self, var):
            raise AttributeError(f"ERROR: '{type(self).__name__}' has already been set.'")
        else:
            setattr(self,var, val)
    
    # Method to retrieve board parameters
    def get_board_val(self,var):
        return getattr(self, var)

    # Main method to instance board connection 
    def load_board(self):
        
        init_sequence_tl040hds20 = bytes()

        board.I2C().deinit()
        
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100_000)
        tft_io_expander = dict(board.TFT_IO_EXPANDER)
        
        # tft_io_expander['i2c_address'] = 0x38 # uncomment for rev B
        
        dotclockframebuffer.ioexpander_send_init_sequence(
            i2c, init_sequence_tl040hds20, **tft_io_expander
        )

        fb = dotclockframebuffer.DotClockFramebuffer(**self._tft_pins, **self._tft_timings)
       
        display = FramebufferDisplay(fb, auto_refresh=False)

        bitmap = displayio.Bitmap(display.width, display.height, 65535)

        self.__setattr__('bitmap', bitmap)
        self.__setattr__('display', display)
        self.__setattr__('i2c', i2c)
        self.__setattr__('fb', fb)
        
