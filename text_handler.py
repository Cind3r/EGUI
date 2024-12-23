class TextHandler:
    
    """ This class handles the logic of setting numerical values to the display as well 
            as outputting information for the second microcontroller to perform the 
            treatment as given parameters. """

    # As of right now, this functions properly when inputting text and clearing
    # however, when hitting done it just clears the value as well. Functionality 
    # needs to be added to export the number to a variable value that stays 
    # stored on the original screen. 

    # TODO: add values that can be exported to a main program
    # TODO: add instancing the starting value so you can edit the parameter
    # TODO: add the main code loop from code.py that loops over values and have that separate from the main program


    def __init__(self, calc_display, clear_button, label_offset):
        self._error = False
        self._calc_display = calc_display
        self._clear_button = clear_button
        self._label_offset = label_offset
        self._accumulator = "0"
        self._done_pressed = False
        self._all_clear()  


    def _all_clear(self):
        self._accumulator = "0"
        self._done_pressed = False
        self._clear_entry()
    
    # Clears the display value
    def _clear_entry(self):
        self._error = False
        self._set_text("0")

    # Sets the display text when entering values
    def _set_text(self, text):
        self._calc_display.text = text
        _, _, screen_w, _ = self._calc_display.bounding_box
        self._calc_display.x = self._label_offset - screen_w*4
    
    # Returns the text value
    def _get_text(self):
        return self._calc_display.text
    
    # Handles input of numerical values
    def _handle_number(self, input_key):
        
        display_text = self._get_text()

        if display_text == "0":
            display_text = ""

        display_text += input_key
        self._set_text(display_text)

        self._done_pressed = False

    # Handles the done button to input the value
    def _handle_done(self):

        self._accumulator = calculate(self._accumulator)
        self._set_text(self._accumulator)
        self._done_pressed = True

    # Handles detection of key pressed
    def add_input(self, input_key):
        try:

            if self._error:
                self._clear_entry()

            elif input_key == "Clear":
                self._all_clear()

            elif input_key == "Clear":
                self._clear_entry() 

            elif len(input_key) == 1:
                self._handle_number(input_key)

            elif input_key == ".":
                if not input_key in self._get_text():
                    self._set_text(self._get_text() + input_key)
                    self._done_pressed = False

            elif input_key == "Done":
                self._handle_done()

        except (ZeroDivisionError, RuntimeError):
            self._all_clear()
            self._error = True
            self._set_text("Error")

def calculate(number_one):
    result = eval(number_one)
    if int(result) == result:
        result = int(result)
    return str(result)