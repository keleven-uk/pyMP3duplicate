###############################################################################################################
#    Copyright (C) <2020>  <Kevin Scott>                                                                      #
#                                                                                                             #
#  A class that acts has a wrapper around a dictionary access.                                               #
#  The items to store are song files,                                                                         #
#    The key is made up of {song.artist}:{tag.title}                                                          #
#    The data is a list [songFile, songDuration]
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
import pickle


class Library():
    """  A simple class that wraps the library dictionary.

         usage:
             songLibrary = myLibrary.Library()

         to add an item              - songLibrary.addItem(key, musicFile, musicDuration)
         to retrieve an item         - songFile, songDuration = songLibrary.getItem(key)
         to test for key             - if songLibrary.hasKey(key):
         to return number of items   - l = songLibrary.noOfItems()

         to load items - songLibrary.load() : this loads using pickle (hard-coded as dup.pickle).
         to save items - songLibrary.save() : this saves using pickle (hard-coded as dup.pickle).

         TODO - possibly needs error checking.
    """

    def __init__(self):
        self.library = {}

    def hasKey(self, key):
        """  Returns true if the key exist in the library.
        """
        return key in self.library

    def addItem(self, key, item1, item2):
        """  Adds to the library at point key, added is a list of items.
             item1 is song duration.
             item2 is song path.
        """
        self.library[key] = [item1, item2]

    def getItem(self, key):
        """  Returns items at position key from the library.
        """
        return self.library[key]

    def noOfItems(self):
        """  Return the number of entries in the library
        """
        return len(self.library)

    def save(self):
        """  Save the library to disc - currently uses pickle.
        """
        with open("dup.pickle", "wb") as f:
            pickle.dump(self.library, f)

    def load(self):
        """  Loads the library from disc - currently uses pickle.
        """
        if os.path.isfile("dup.pickle"):
            with open("dup.pickle", "rb") as f:
                self.library = pickle.load(f)