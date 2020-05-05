###############################################################################################################
#    myTimer.py   Copyright (C) <2020>  <Kevin Scott>                                                         #
#                                                                                                             #
#    Inspired by https://realpython.com/python-timer/                                                         #
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

import time

class TimerError(Exception):
    """  A custom exception used to report errors in use of Timer class.
    """

class Timer():
    """  A simple timer.

        t.start     - will start the timer.
        t.eplapsed  - will return the elapsed time since the time started.
        t.stop      - will return the time since the time started and stop the timer.

        The methods have been converted to property's, makes the syntax cleaner.

        Will raise an exception is there is an error.
    """
    def __init__(self):
        self._start_time = None

    @property
    def Start(self):
        """  Start a new timer.
        """
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop to stop it")

        self._start_time = time.perf_counter()

    @property
    def Elapsed(self):
        """  Return the elapsed time since start, but does not stop the timer.
        """
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start to start it")

        _elapsed_time = time.perf_counter() - self._start_time
        return f"{_elapsed_time:0.3f}"

    @property
    def Stop(self):
        """  Stop the timer, and report the elapsed time.
        """
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start to start it")

        _elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return f"{_elapsed_time:0.3f}"