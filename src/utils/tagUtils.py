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

import colorama
import eyed3

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from tinytag import TinyTag
from libindic.soundex import Soundex

import src.utils.duplicateUtils as duplicateUtils
import src.Exceptions as myExceptions

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
        logger.error(f"ERROR : Can't read tags : {musicFile} : {e.message}")
        return False
    artist1 = duplicateUtils.removeThe(tags.artist)
    title1 = duplicateUtils.removeThe(tags.title)

    try:  # Tries to read tags from the music file.
        tags = TinyTag.get(songFile)
    except Exception as e:  # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {songFile} : {e.message}")
        return False
    artist2 = duplicateUtils.removeThe(tags.artist)
    title2  = duplicateUtils.removeThe(tags.title)

    return True if (artist1 == artist2) and (title1 == title2) else False

####################################################################################### scanTags ##############
def scanTags(tag, musicFile, soundex, logger):
    """  Scans the musicfile for the required tags.
         Will use the method indicated in the user configure.

         If there is a problem reading the tags, raise an exception.
    """
    match tag:
        case "tinytag":
            try:  # Tries to read tags from the music file.
                tags = TinyTag.get(musicFile)
            except Exception as error:  # Can't read tags - flag as error.
                logger.error(f"Tinytag error reading tags :: {musicFile}  : {error.message} ")
                raise myExceptions.TagReadError(f"Tinytag error reading tags {musicFile}  : {error.message}") from error
            artist    = duplicateUtils.removeThe(tags.artist)
            title     = duplicateUtils.removeThe(tags.title)
            duration  = tags.duration
            duplicate = ""

        case "eyed3":
            try:
                tags = eyed3.load(musicFile)
            except Exception as error:
                logger.error(f"Eyed3 error reading tags :: {musicFile}  : {error.message}")
                raise myExceptions.TagReadError(f"Eyed3 error reading tags {musicFile}  : {error.message}") from error
            artist    = duplicateUtils.removeThe(tags.tag.artist)
            title     = duplicateUtils.removeThe(tags.tag.title)
            duration  = tags.info.time_secs
            duplicate = ""

        case "mutagen":
            try:
                tags  = ID3(musicFile)
                audio = MP3(musicFile)
            except Exception as error:
                logger.error(f"Nutagen error reading tags :: {musicFile}  : {error.message} ")
                raise myExceptions.TagReadError(f"Mutagen error reading tags {musicFile} : {error.message}") from error
            artist   = duplicateUtils.removeThe(tags["TPE1"][0])
            title    = duplicateUtils.emoveThe(tags["TIT2"][0])
            duration = audio.info.length
            try:  # Try to read duplicate tag.
                duplicate = tags["TXXX:DUPLICATE"][0]  # Ignore if not there.
            except:
                duplicate = ""
        case _:
            # Should not happen, tinytag should be returned by default.
            logger.error("Unknown user option for Tags Module.")
            print(f"{colorama.Fore.RED}Unknown user option for Tags Module.{colorama.Fore.RESET}")
            exit(4)

    if not duration:  # In case there is no valid duration time on the mp3 file.
        musicDuration = 0
    else:
        musicDuration = round(duration, 2)

    key = phonetic.soundex(f"{artist}:{title}") if soundex else f"{artist}:{title}"
    return key, musicDuration, duplicate, artist, title
