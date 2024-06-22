
from datetime import datetime

class Logger():

    def __init__(self, debug = True):
        self.debug = debug

    def error(self, message):
        if self.debug:
            error_string = "ERROR - " + str(datetime.now()) + " - " + message
            print(error_string)

    def info(self, message):
        if self.debug:
            info_string = "INFO - " + str(datetime.now()) + " - " + message
            print(info_string)

    