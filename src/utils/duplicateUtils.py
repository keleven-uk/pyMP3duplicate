###############################################################################################################
#    duplicateUtils.py   Copyright (C) <2020-2021>  <Kevin Scott>                                             #                                                                                                             #                                                                                                             #
#    A number of helper and utility functions                                                                 #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020-2021>  <Kevin Scott>                                                                 #
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
from libindic.soundex import Soundex

import src.myLicense as myLicense

phonetic = Soundex()

####################################################################################### removeThe #############
def removeThe(name):
    """  Removes 'the' from the from the beginning of artist and title if present.
         Mainly a problem with artist, to be honest.
         Name is returned lower case.
    """
    if name:
        n = name.lower()
        return name[4:] if n.startswith("the") else name
    else:
        return ""

####################################################################################### checkThe #############
def trailingThe(name):
    """   Checks the name for a trailing the, i.e.  'Shadows, the' instead of The Shadows.
          Returns True is found else returns False.
    """

    if name:
        n = name.lower()
        return n.endswith(", the")

####################################################################################### createKey #############
def createKey(artist, title, soundex):
    """ Creates the key from the artist and title.
        key is either formed from string substitution or created from the soundex of the string.
    """
    return phonetic.soundex(f"{artist}:{title}") if soundex else f"{artist}:{title}"


######################################################################################## loadExplorer() ######
def loadExplorer(logger):
    """  Load program working directory into file explorer.
    """
    try:
        os.startfile(os.getcwd(), "explore")
    except NotImplementedError as error:
        logger.error(error)
    exit(0)
