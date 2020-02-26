###############################################################################################################
#                                                                                                             #
#  A Wrapper for logging - based on https://www.toptal.com/python/in-depth-python-logging                     #
#                                                                                                             #
#       Kevin Scott     2020                                                                                  #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020>  <Kevin Scott>                                                                      #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either myVERSION 3 of the       #
#    License, or (at your option) any later myVERSION.                                                        #
#                                                                                                             #
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without        #
#    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#    GNU General Public License for more details.                                                             #
#                                                                                                             #
#    You should have received a copy of the GNU General Public License along with this program.               #
#    If not, see <http://www.gnu.org/licenses/>.                                                              #
#                                                                                                             #
###############################################################################################################

import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from _version import myNAME

FORMATTER = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
                                                                 # Could add if needed - %(funcName)s:%(lineno)d
LOG_FILE = f"{myNAME}.log"

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=7)  # Only keep 7 previous logs.
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)              # better to have too much log than not enough
    #logger.addHandler(get_console_handler())   # add tp log to console
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger