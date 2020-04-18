###############################################################################################################
#    myConfig.py    Copyright (C) <2020>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A class that acts has a wrapper around the config file - config.toml.                                    #
#    The config file is first read, then the properties are made available.                                   #
#    The config file is currently in toml format.                                                             #
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

import os
import toml
import colorama


class Config():
    """  A class that acts has a wrapper around the config file - config.toml.
         The config file is hard coded and lives in the save directory has the main script.
         The config file is first read, then the properties are made available.

         If config.toml is not found, a default config file is generated.

         Use single quotes :-(

         usage:
            myConfig = myConfig.Config()
    """

    FILE_NAME = "config.toml"


    def __init__(self):
        try:
            self.config = toml.load(self.FILE_NAME)      # Load the config file, in toml
        except FileNotFoundError:
            print(f"{colorama.Fore.RED}Config not found. {colorama.Fore.RESET}")
            print(f"{colorama.Fore.YELLOW}Writing default config file. {colorama.Fore.RESET}")
            self.writeDefaultConfig()
            print(f"{colorama.Fore.GREEN}Running program with default config. {colorama.Fore.RESET}")

    def NAME(self):
        """  Returns application name.
        """
        return self.config['INFO']['myNAME']

    def VERSION(self):
        """  Returns application Version.
        """
        return self.config['INFO']['myVERSION']

    def NCOLS(self):
        """  Returns Max number of columns for tqdm [width of progress bar].
        """
        return self.config['TQDM']['ncols']

    def TAGS(self):
        """  Returns the module used to scan the mp3 tags.
             Currently supports three modules tinytag, mutagen or eyed3.
             Will default to tinytag, if module returns other.
        """
        module = self.config['TAGS']['module']

        if module == "mutagen" or module == "eyed3":
            return module
        else:
            return "tinytag"

    def IGNORE(self):
        """  Returns the ignore marker.
             if both duplicate have this in comment, then ignore
        """
        return self.config['TAGS']['ignore']

    def SOUNDEX(self):
        """  Returns the Soundex marker.
             if true, uses Soundex for tags matching else use normal strings.
        """
        return self.config['TAGS']['soundex']

    def DB_NAME(self):
        """  Returns the location and filename of the database.
             if location is empty will use just filename, so save next to main script.
        """
        location = self.config['DATABASE']['location']

        if not location:
            return self.config['DATABASE']['filename']
        else:
            return f"{location}\{self.config['DATABASE']['filename']}"


    def writeDefaultConfig(self):
        """ Write a default config file.
            This is hard coded  ** TO KEEP UPDATED **
        """
        config = dict()

        config['INFO'] = {'myVERSION': '1.1.3g',
                          'myNAME'   : 'pyMP3duplicate'}

        config['TQDM'] = {'ncols': 160}

        config['TAGS'] = {'module' : 'tinytag',
                          'ignore' : '**IGNORE**',
                          'soundex': true}

        config['DATABASE'] = {'filename': 'dup.pickle',
                              'location': ''}

        st_toml = toml.dumps(config)

        with open(self.FILE_NAME, "w") as configFile:
            configFile.writelines(st_toml)


        self.config = toml.load(self.FILE_NAME)      # Load the config file, in toml
