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

import time
import json
import pickle
import pprint
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
         to load items - songLibrary.load(filename) : this loads using pickle (located at filename).
         to save items - songLibrary.save(filename) : this saves using pickle (located at filename).

         TODO - possibly needs error checking.
    """

    def __init__(self):
        self.library = {}

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
        del self.library[key]

    def noOfItems(self, filename, format):
        """  Return the number of entries in the library
        """
        if not self.library:
            self.load(filename, format)
        return len(self.library)

    def save(self, filename, format):
        """  Save the library to disc.
        """
        if format == "pickle":
            self.pickleSave(filename)
        else:
            self.jsonSave(filename)

    def load(self, filename, format):
        """  Loads the library from disc.
        """
        if format == "pickle":
            self.pickleLoad(filename)
        else:
            self.jsonLoad(filename)

    def check(self, filename, mode, format):
        """  Runs a database data integrity check.
        """
        startTime = time.time()
        duplicates = 0
        removed    = 0
        print(f"Running database integrity check on {filename} in {mode} mode")

        print(f"Loading {filename}")
        self.load(filename, format)

        l = self.noOfItems(filename, format)
        print(f"Song Library has {l} songs")

        for song in self.library.copy():                 #  iterate over a copy, gets around the error dictionary changed size during iteration
            path, duration, ignore = self.getItem(song)
            if not path.exists():
                if mode == "delete":
                    self.delItem(song)
                    print(f"Deleting {path}")
                    removed += 1
                else:
                    duplicates += 1
                    print(f"Song does not exist {path}")

        elapsedTimeSecs = time.time() - startTime

        if removed:
            print(f"Saving {filename}")
            self.save(filename, format)
            print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and removed {removed} entries from database.")
            l = self.noOfItems(filename, format)
            print(f"Song Library has now {l} songs")
        else:
            if duplicates:
                print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and found {duplicates} duplicates songs.")
            else:
                print(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} and database looks good.")


#------------- pickle load and save. ------------------
    def pickleLoad(self, filename):
        """  Load the song library in pickle format.
        """
        if filename.exists():
            with open(filename, "rb") as f:
                self.library = pickle.load(f)

    def pickleSave(self, filename):
        """  Save the song library in pickle format.
        """
        with open(filename, "wb") as f:
            try:
                pickle.dump(self.library, f)
            except FileNotFoundError:
                print("ERROR :: Cannot find library file.")
#------------- json load and save. ------------------
    def jsonLoad(self, filename):
        """  Load the song library in json format.
        """
        if filename.exists():
            with open(filename, "r") as json_file:
                self.library = json.load(json_file)

    def jsonSave(self, filename):
        """  Save the song library in json format.
        """

        print(f"{filename}")
        with open(filename, "w") as json_file:
            try:
                json.dump(self.library, json_file)
            except FileNotFoundError:
                print("ERROR :: Cannot find library file.")
