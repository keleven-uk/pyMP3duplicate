###############################################################################################################
#    myLibrary.py   Copyright (C) <2020>  <Kevin Scott>                                                       #
#                                                                                                             #
#    A class that acts has a wrapper around a dictionary access.                                              #
#    The items to store are song files,                                                                       #
#      The key is either made up of {song.artist}:{tag.title}                                                 #
#        or soundex({song.artist}:{tag.title})                                                                #
#        or any unique token generated from the song.                                                         #
#      The data is a list [songFile, songDuration, ignore flag]                                               #
#                                                                                                             #
#    Uses pickle to load and save the library.                                                                #
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

import os
import time
import json
import pickle
import datetime
import pathlib


class Library():
    """  A simple class that wraps the library dictionary.

         usage:
         songLibrary = myLibrary.Library()

         to add an item              - songLibrary.addItem(key, musicFile, musicDuration)
         to retrieve an item         - songFile, songDuration, songDuplicate = songLibrary.getItem(key)
         to test for key             - if songLibrary.hasKey(key):
         to return number of items   - l = songLibrary.noOfItems()
         to test database integrity  - songLibrary.check("test")
         to prune database           - songLibrary.check("delete")
         to load items               - songLibrary.load()
         to save items               - songLibrary.save()

         TODO - possibly needs error checking.
    """

    def __init__(self, DBfilename, DBformat):
        self.library     = {}
        self.__filename  = pathlib.Path(DBfilename)
        self.__format    = DBformat
        self.__overWrite = True     #  Originally set to overwrite DB file.


    def hasKey(self, key):
        """  Returns true if the key exist in the library.
        """
        return key in self.library


    def addItem(self, key, item1, item2, item3):
        """  Adds to the library at point key, added is a list of items.
             item1 is song path.
             item2 is song duration.
             item3 is song ignore flag.
        """
        self.library[key] = [item1, item2, item3]


    def getItem(self, key):
        """  Returns items at position key from the library.
        """
        return self.library[key]


    def delItem(self, key):
        """  Deletes item at position key from the library.
        """
        try:
            del self.library[key]
        except (KeyError):
            print(f"ERROR : Library has no key : {key}")


    @property
    def noOfItems(self):
        """  Return the number of entries in the library
        """
        if not self.library:
            self.load()
        return len(self.library)


    def DBOverWrite(self, mode):
        """  If set to True the old database file, if exists, will be overwritten.
             If set to False the old database file will be backed up before new one is written.
        """
        self.__overWrite = mode


    def save(self):
        """  Save the library to disc.
        """
        if self.__format == "pickle":
            self.pickleSave()
        else:
            self.jsonSave()


    def load(self):
        """  Loads the library from disc.
        """
        if self.__format == "pickle":
            self.pickleLoad()
        else:
            self.jsonLoad()


    def check(self, mode):
        """  Runs a database data integrity check.
        """
        startTime = time.time()
        missing   = 0
        removed   = 0
        print(f"Running database integrity check on {self.__filename} in {mode} mode")

        print(f"Loading {self.__filename}")
        if not self.library:
            self.load()

        l = self.noOfItems
        print(f"Song Library has {l} songs")

        for song in self.library.copy():                 #  iterate over a copy, gets around the error dictionary changed size during iteration
            path, duration, ignore = self.getItem(song)
            if not os.path.isfile(path):
                if mode == "delete":
                    self.delItem(song)
                    print(f"Deleting {path}")
                    removed += 1
                else:
                    missing += 1
                    print(f"Song does not exist {path}")

        elapsedTimeSecs = time.time() - startTime

        if removed:
            print(f"Saving {self.__filename}")
            self.save()
            print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and removed {removed} entries from database.")
            l = self.noOfItems
            print(f"Song Library has now {l} songs")
        else:
            if missing:
                print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and found {missing} missing songs.")
            else:
                print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and database looks good.")


#------------- pickle load and save. ------------------
    def pickleLoad(self):
        """  Load the song library in pickle format.
        """
        try:
            with open(self.__filename, "rb") as pickle_file:
                self.library = pickle.load(pickle_file)
        except FileNotFoundError:
            print(f"ERROR :: Cannot find library file. {self.__filename}")
            exit(0)

    def pickleSave(self):
        """  Save the song library in pickle format.
        """
        if not self.__overWrite:
            if self.__filename.exists():
                now = datetime.datetime.now()
                self.__filename.rename(str(self.__filename) + "." + now.strftime("%Y%m%d%H%M%S"))
        with open(self.__filename, "wb") as pickle_file:
            pickle.dump(self.library, pickle_file)

#------------- json load and save. ------------------
    def jsonLoad(self):
        """  Load the song library in json format.
        """
        try:
            with open(self.__filename, "r") as json_file:
                self.library = json.load(json_file)
        except FileNotFoundError:
            print("ERROR :: Cannot find library file.")
            exit(0)

    def jsonSave(self):
        """  Save the song library in json format.
        """
        if not self.__overWrite:
            if self.__filename.exists():
                now = datetime.datetime.now()
                self.__filename.rename(str(self.__filename) + "." + now.strftime("%Y%m%d%H%M%S"))
        with open(self.__filename, "w") as json_file:
            json.dump(self.library, json_file, indent=4)
