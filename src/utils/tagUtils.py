###############################################################################################################
#    tagUtils.py   Copyright (C) <2020-2022>  <Kevin Scott>                                                   #                                                                                                             #                                                                                                             #
#    A number of helper and utility functions around reading ID3 tags from mp3 files.                         #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2020-2022>  <Kevin Scott>                                                                 #
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

from tinytag import TinyTag
from libindic.soundex import Soundex

import src.utils.duplicateUtils as duplicateUtils

phonetic = Soundex()

####################################################################################### checktags #############
def checkTags(musicFile, songFile, logger):
    """  Used to check if the Soundex algorithm has returned a false positive.
         Returns True if the artist and title of the two songs are the same.
         Returns False if there is an error.
    """
    try:  # Tries to read tags from the music file.
        tags = TinyTag.get(musicFile)
    except Exception as e:  # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {musicFile}")
        return False
    artist1 = duplicateUtils.removeThe(tags.artist)
    title1 = duplicateUtils.removeThe(tags.title)

    try:  # Tries to read tags from the music file.
        tags = TinyTag.get(songFile)
    except Exception as e:  # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {songFile}")
        return False
    artist2 = duplicateUtils.removeThe(tags.artist)
    title2  = duplicateUtils.removeThe(tags.title)

    return True if (artist1 == artist2) and (title1 == title2) else False

####################################################################################### scanTags ##############
def scanTags(musicFile):
    """  Scans the musicfile for the required tags.
         Will use the method indicated in the user configure.

         If there is a problem reading the tags, raise an exception.
    """
    try:  # Tries to read tags from the music file.
        tags = TinyTag.get(musicFile)
    except Exception as e:  # Can't read tags - flag as error.
        logger.error(f"Tinytag error reading tags :: {e} ")
        raise myExceptions.TagReadError(f"Tinytag error reading tags {musicFile}")
    artist    = duplicateUtils.removeThe(tags.artist)
    title     = duplicateUtils.removeThe(tags.title)
    duration  = tags.duration
    duplicate = ""


    if not duration:  # In case there is no valid duration time on the mp3 file.
        musicDuration = 0
    else:
        musicDuration = round(duration, 2)

    key = phonetic.soundex(f"{artist}:{title}")
    return key, musicDuration, duplicate, artist, title
