###############################################################################################################
#    duplicateUtils.py   Copyright (C) <2020-2023>  <Kevin Scott>                                             #                                                                                                             #                                                                                                             #
#    A number of helper and utility functions                                                                 #
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

import os
import sys
import colorama

from tqdm import tqdm
from plyer import notification

import src.License as License
import src.Exceptions as myExceptions

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
    else:
        return ""


######################################################################################## loadExplorer() ######
def loadExplorer(logger):
    """  Load program working directory into file explorer.
    """
    try:
        os.startfile(os.getcwd(), "explore")
    except NotImplementedError as error:
        logger.error(error)
    sys.exit(0)


####################################################################################### checkToIgnore #########
def checkToIgnore(musicDuplicate, songDuplicate, ignore):
    """  Each song may carry a ignore flag, return True if these are the same.
         Only checked if the tags are read using mutagen.
    """
    return (musicDuplicate == ignore) and (songDuplicate == ignore)


####################################################################################### countSongs ############
def countSongs(sourceDir, fileList, NCOLS):
    """  Count the number of songs [.mp3 files] in the sourceDir.
         The filenames are saved in a list fileList, this is then passed to scanMusic.
         Takes just over a second at 160000 files approx.
    """
    print("Counting Songs")
    for musicFile in tqdm(sourceDir.rglob("*.mp3"), unit="songs", ncols=NCOLS, position=1):
        fileList.append(musicFile)

    print(f"... with a song count of {len(fileList)}")
    return len(fileList)


####################################################################################### printDuplicate ########
def logTextLine(textLine, textFile, logger=None):
    """  if the textFile is set, then write the line of text to that file, else print to screen.

         textLine needs to be a string, for f.write - NOT a path.

         If a logger is passed in, then use it - else ignore.
    """
    if textFile:
        with open(textFile, encoding="utf-8", mode="a") as f:     # Open in amend mode, important.
            f.write(textLine + "\n")
    else:
        print(textLine)

    if logger:
        logger.info(textLine)

######################################################################################## checkDatabase() ######
def checkDatabase(songLibrary, check, dfile, logger, appName, appVersion, icon, timeout, NOTIFICATION):
    """  Perform a data integrity check on the library.

          if check == test then just report errors.
          if check == delete then report errors and delete entries.
    """
    if NOTIFICATION:
        notification.notify(appName, "Database Check Started", appName, icon, timeout)

    License.printShortLicense(appName, appName, dfile, False)

    try:
        songLibrary.check(check, logger)
    except myExceptions.LibraryError:
        message = f"{colorama.Fore.RED}ERROR : No Database file found. {colorama.Fore.RESET}"
        print(message)
        if logger:
            logger.info(message)
        sys.exit(1)

    print("Goodbye.")
    if NOTIFICATION:
        notification.notify(appName, "Database Check Ended", appName, icon, timeout)

    sys.exit(0)

#(Config.NAME, message, Config.NAME, icon, timeout)
