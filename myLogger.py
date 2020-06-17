###############################################################################################################
#    myLogger.py   Kevin Scott     2020                                                                       #
#                                                                                                             #
#    A Wrapper for logging - based on https://www.toptal.com/python/in-depth-python-logging                   #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020>  <Kevin Scott>                                                                      #
#                                                                                                             #
#    This program is free software: you can redistribute it and/or modify it under the terms of the           #
#    GNU General Public License as published by the Free Software Foundation, either Version 3 of the         #
#    License, or (at your option) any later Version.                                                          #
#                                                                                                             #
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without        #
#    even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#    GNU General Public License for more details.                                                             #
#                                                                                                             #
#    You should have received a copy of the GNU General Public License along with this program.               #
#    If not, see <http://www.gnu.org/licenses/>.                                                              #
#                                                                                                             #
###############################################################################################################

"""
    usage:
        logger = myLogger.get_logger(myConfig.NAME() + ".log")

    to write to log - log.debug(text message) [also can use log, error, info, warning, critical & exception]

    can add exc_info=True to include exception information, not needed with log.exception
"""

import sys
import logging
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
                                                                 # Could add if needed - %(funcName)s:%(lineno)d
def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_file_handler(logger_name):
    file_handler = TimedRotatingFileHandler(logger_name, when="midnight", backupCount=7)  # Only keep 7 previous logs.
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)              # better to have too much log than not enough
    #logger.addHandler(get_console_handler())   # add to log to console
    logger.addHandler(get_file_handler(logger_name))
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
