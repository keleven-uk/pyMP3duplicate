#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020>  <Kevin Scott>                                                                      #
#                                                                                                             #
#  A class that acts has a wrapper around the config file - config.toml.                                      #
#  The config file is first read, then the properties are made available.                                     #
#  The config file is currently in toml format.
#                                                                                                             #
###############################################################################################################
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

import toml

class Config():
    """  A class that acts has a wrapper around the config file - config.toml.                                    #
         The config file is first read, then the properties are made available.

         Use single quotes :-(
    """

    def __init__(self):
        self.config = toml.load("config.toml")      # Load the config file, in toml

    def NAME(self):
        """  Returns application name.
        """
        return self.config['INFO']['myNAME']

    def VERSION(self):
        """  Returns application Version.
        """
        return self.config['INFO']['myVERSION']

    def ITERATIONS(self):
        """  Returns application Version.
        """
        return self.config['LOOP']['Iterations']
