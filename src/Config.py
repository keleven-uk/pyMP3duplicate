###############################################################################################################
#    myConfig.py    Copyright (C) <2020-2023>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A class that acts has a wrapper around the configure file - config.toml.                                 #
#    The configure file is first read, then the properties are made available.                                #
#    The configure file is currently in toml format.                                                          #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020-2023>  <Kevin Scott>                                                                      #
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

import toml
import colorama


class Config():
    """  A class that acts has a wrapper around the configure file - config.toml.
         The configure file is hard coded and lives in the same directory has the main script.
         The configure file is first read, then the properties are made available.

         If config.toml is not found, a default configure file is generated.

         Use single quotes :-(

         usage:
            myConfig = myConfig.Config()
    """

    FILE_NAME = "config.toml"

    def __init__(self):
        try:
            with open(self.FILE_NAME, "r") as configFile:       # In context manager.
                self.config = toml.load(configFile)             # Load the configure file, in toml.
        except FileNotFoundError:
            print(f"{colorama.Fore.RED}Configure file not found. {colorama.Fore.RESET}")
            print(f"{colorama.Fore.YELLOW}Writing default configure file. {colorama.Fore.RESET}")
            self._writeDefaultConfig()
            print(f"{colorama.Fore.GREEN}Running program with default configure settings. {colorama.Fore.RESET}")
        except toml.TomlDecodeError:
            print(f"{colorama.Fore.RED}Error reading configure file. {colorama.Fore.RESET}")
            print(f"{colorama.Fore.YELLOW}Writing default configure file. {colorama.Fore.RESET}")
            self._writeDefaultConfig()
            print(f"{colorama.Fore.GREEN}Running program with default configure settings. {colorama.Fore.RESET}")

    @property
    def NAME(self):
        """  Returns application name.
        """
        return self.config["INFO"]["myNAME"]

    @property
    def VERSION(self):
        """  Returns application Version.
        """
        return self.config["INFO"]["myVERSION"]

    @property
    def NOTIFICATION(self):
        """  Returns the [system tray] Notification marker.
        """
        return self.config["APPLICATION"]["notification"]

    @property
    def NCOLS(self):
        """  Returns Max number of columns for tqdm [width of progress bar].
        """
        return self.config["TQDM"]["ncols"]

    @property
    def TAGS(self):
        """  Returns the module used to scan the mp3 tags.
             Currently supports three modules tinytag, mutagen or eyed3.
             Will default to tinytag, if module returns other.
        """
        module = self.config["TAGS"]["module"]

        if module == "mutagen" or module == "eyed3":
            return module
        else:
            return "tinytag"

    @property
    def IGNORE(self):
        """  Returns the ignore marker.
             if both duplicate have this in comment, then ignore
        """
        return self.config["TAGS"]["ignore"]

    @property
    def SOUNDEX(self):
        """  Returns the Soundex marker.
             if true, uses Soundex for tags matching else use normal strings.
        """
        return self.config["TAGS"]["soundex"]

    @property
    def DB_FORMAT(self):
        """  Returns the format of the song library - either pickle or json.
        """
        format = self.config["DATABASE"]["format"]

        if format == "json":
            return "json"
        else:
            return "pickle"

    @property
    def DB_NAME(self):
        """  Returns the location and filename of the database.
             if location is empty will use just filename, so save next to main script.
        """
        location  = self.config["DATABASE"]["location"]
        filename  = self.config["DATABASE"]["filename"]
        extension = self.config["DATABASE"]["format"]

        if location:
            return f"{location}\\{filename}.{extension}"
        else:
            return f"{filename}.{extension}"

    @property
    def DB_LOCATION(self):
        """  Returns the location [path] of the database.
             If empty, then save in the same directory has the script.
        """
        return self.config["DATABASE"]["location"]

    @property
    def DB_OVERWRITE(self):
        """  If set to True the old database file, if exists, will be overwritten.
             If set to False the old database file will be backed up before new one is written.
        """
        return self.config["DATABASE"]["overwrite"]

    @property
    def ZAP_RECYCLE(self):
        """  If set to True the recycle bin will be used for deletes.
             If set to False all deletes are final :-(.
        """
        return self.config["ZAP"]["recycle"]

    @property
    def EMPTY_DIR(self):
        """  If set to True then delete empty directories.
             If set to False ignore empty directories
        """
        return self.config["ZAP"]["emptyDir"]

    def _writeDefaultConfig(self):
        """ Write a default configure file.
            This is hard coded  ** TO KEEP UPDATED **
        """
        config = dict()

        config["INFO"] = {"myVERSION": "2024.49",
                          "myNAME"   : "pyMP3duplicate"}

        config["APPLICATION"] = {"notification": True}

        config["TQDM"] = {"ncols": 160}

        config["TAGS"] = {"module" : "tinytag",
                          "ignore" : "**IGNORE**",
                          "soundex": True}

        config["DATABASE"] = {"format"   : "pickle",
                              "filename" : "dup",
                              "location" : "",
                              "overwrite": False}

        config["ZAP"] = {"recycle" : True,
                         "emptyDir": True}

        st_toml = toml.dumps(config)

        with open(self.FILE_NAME, "w") as configFile:       # In context manager.
            configFile.write("#   Configure files for pyMP3duplicates.py \n")
            configFile.write("#\n")
            configFile.write("#   true and false are lower case \n")
            configFile.write("#   Configure files for pyMP3duplicates.py \n")
            configFile.write("#   location needs double \ i.e. c:\\tmp\\music - well, on windows any way. \n")
            configFile.write("#\n")
            configFile.write("#   <2020-2023> (c) Kevin Scott \n")
            configFile.write("\n")
            configFile.writelines(st_toml)                  # Write configure file.

        with open(self.FILE_NAME, "r") as configFile:       # In context manager.
            self.config = toml.load(configFile)             # Load the configure file, in toml.
