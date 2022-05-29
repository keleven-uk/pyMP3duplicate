###############################################################################################################
#    pyMP3duplicate   Copyright (C) <2020-2022>  <Kevin Scott>                                                #                                                                                                             #                                                                                                             #
#    The program will scan a given directory and report duplicate MP3 files.                                  #
#                                                                                                             #
#  Usage:                                                                                                     #
# pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-fA DUPFILEAMEND] [-d DIFFERENCE] [-b] [-n] [-l]        #
#                                                              [-v] [-e] [-c] [-cD] [-xL] [-xS] [-np] [-zD]   #
#                                                                                                             #
#     For changes see history.txt                                                                             #
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

from pathlib import Path
from plyer import notification
from alive_progress import alive_bar

import src.args as args
import src.Timer as Timer
import src.Config as Config
import src.Logger as Logger
import src.License as License
import src.Library as Library
import src.Exceptions as Exceptions
import src.utils.zapUtils as zapUtils
import src.utils.tagUtils as tagUtils
import src.utils.duplicateUtils as duplicateUtils

#try:
    #import pyjion       #  Apparently tries to improve speed.
    #pyjion.enable()
#except:
    #pass


####################################################################################### scanMusic #############
def scanMusic(mode, fileList, duplicateFile, difference, songsCount, noPrint, checkThe, soundex, tagType):
    """  Scan the list fileList, which should contain mp3 files only.
         The songs are added to the library using the song artist and title as key.
         If the song already exists in the library, then the two are checked.

         mode = "scan"  -- the fileList is scanned and duplicates are reported.
         mode = "build" -- the fileList is scanned and the database is built only, duplicates are not checked.

         Uses tqdm - a very cool progress bar for console windows.
         Now uses alive_bar a even more cool progress bar for console windows.
    """
    count      = 0  # Number of song files to check.
    duplicates = 0  # Number of duplicate songs.
    noDups     = 0  # Number of duplicate songs that fall outside of the time difference.
    ignored    = 0  # Number of duplicate songs that have been marked to ignore.
    falsePos   = 0  # Number of songs that seem to be duplicate, but ain't.
    noTrailing = 0  # Number of songs that have a trailing the  i.e.  Shadows, the instead of The Shadows.

    with alive_bar(songsCount, bar="circles", spinner="notes") as bar:
        for musicFile in fileList:

            try:
                key, musicDuration, musicDuplicate, artist, title = tagUtils.scanTags(Config.TAGS, musicFile, soundex)
            except Exception as e:  # Can't read tags - flag as error.
                logger.error(f"Raised exception at calling scanTags :: {e} ")
                continue

            if songLibrary.hasKey(key):
                if mode == "build": continue  # Only analyse songs if in scan mode.

                songFile, songDuration, songDuplicate = songLibrary.getItem(key)

                if abs(musicDuration - songDuration) < difference:
                    if tagType == "mutagen":  # Using mutagen, we should check for ignore flag
                        if duplicateUtils.checkToIgnore(musicDuplicate, songDuplicate, Config.IGNORE):
                            ignored += 1
                            continue  # Do not print ignore duplicate
                    message = " Duplicate Found "
                    if soundex and not tagUtils.checkTags(musicFile, songFile, logger):
                        falsePos += 1
                        if not noPrint:
                            message = " Possible False Positive "
                        else:
                            continue  # Do not print Possible False Positives
                    duplicateUtils.logTextLine("-" * 70 + message + "-" * 40, duplicateFile)
                    duplicateUtils.logTextLine(f"{musicFile} {timer.formatSeconds(musicDuration)}", duplicateFile)
                    duplicateUtils.logTextLine(f"{songFile}  {timer.formatSeconds(songDuration)}", duplicateFile)
                    duplicates += 1
                else:  # if abs(musicDuration - songDuration) < difference:
                    noDups += 1

            else:  # if songLibrary.hasKey(key):  Song is a new find, add to database.

                if checkThe and duplicateUtils.trailingThe(artist):         #  A new artist, check for trailing the.
                    duplicateUtils.logTextLine("-" * 70 + " Trailing the found " + "-" * 40, duplicateFile)
                    duplicateUtils.logTextLine(f"{artist} is wrong in {musicFile}.", duplicateFile)
                    noTrailing +=1

                songLibrary.addItem(key, os.fspath(musicFile), musicDuration, musicDuplicate)

            bar()   #  Update alive_bar.

    count = songLibrary.noOfItems + noDups + duplicates  # Adjust for duplicates found.

    zapUtils.removeUnwanted(sourceDir, duplicateFile, Config.EMPTY_DIR, zap, Config.ZAP_RECYCLE, logger)

    duplicateUtils.logTextLine("", duplicateFile)
    if mode == "build":
        duplicateUtils.logTextLine(f"{count} music files found.", duplicateFile)
    elif ignored:
        duplicateUtils.logTextLine(f"{count} music files found with {duplicates} duplicates, with {ignored} songs.", duplicateFile)
    else:
        duplicateUtils.logTextLine(f"{count} music files found with {duplicates} duplicates.", duplicateFile)

    if noDups:
        duplicateUtils.logTextLine(f" Found possible {noDups} duplicates, but with a time difference greater then {difference}.", duplicateFile)

    if noTrailing:
        duplicateUtils.logTextLine(f" Found possible {noTrailing} artists with a trailing 'the' in their name.", duplicateFile)

    if falsePos:
        if noPrint:
            duplicateUtils.logTextLine(f" Found possible {falsePos} false positives [not displayed].", duplicateFile)
        else:
            duplicateUtils.logTextLine(f" Found possible {falsePos} false positives.", duplicateFile)


############################################################################################### __main__ ######

if __name__ == "__main__":

    icon    = "resources\\tea.ico"  # icon used by notifications
    timeout = 5  # timeout used by notifications in seconds

    Config = Config.Config()  # Need to do this first.

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        runningInfo = ('running in a PyInstaller bundle')
        DBpath = Path(Config.DB_LOCATION + Config.DB_NAME)
        LGpath = Config.NAME +".log"                     #  Must be a string for a logger path.
        icon   = ""                                      # icon used by notifications
    else:
        runningInfo = ('running in a normal Python process')
        DBpath = Path("data", Config.DB_LOCATION + Config.DB_NAME)
        LGpath = "data\\" +Config.NAME +".log"                     #  Must be a string for a logger path.
        icon   = "resources\\tea.ico"                              # icon used by notifications

    songLibrary = Library.Library(DBpath, Config.DB_FORMAT)  # Create the song library.
    logger      = Logger.get_logger(LGpath)                    # Create the logger.
    timer       = Timer.Timer()

    sourceDir, duplicateFile, noLoad, noSave, build, difference, noPrint, zap, checkThe, checkDB = args.parseArgs(Config.NAME, Config.VERSION, logger)

    if checkDB == 1:
        duplicateUtils.checkDatabase(songLibrary, "test", DBpath, logger, Config.NAME, Config.VERSION, icon, timeout, Config.NOTIFICATION)          # Run data integrity check in test mode on library.
    elif checkDB == 2:
        duplicateUtils.checkDatabase(songLibrary, "delete", DBpath, logger, Config.NAME, Config.VERSION, icon, timeout, Config.NOTIFICATION)        # Run data integrity check in delete mode on library.

    timer.Start

    if Config.SOUNDEX:
        mode = f"Using Soundex for {Config.TAGS} matching"
    else:
        mode = f"Using Strings for {Config.TAGS} matching"

    message = f"Start of {Config.NAME} {Config.VERSION}"

    if Config.NOTIFICATION: notification.notify(Config.NAME, message, Config.NAME, icon, timeout)
    logger.info("-" * 100)
    logger.info(message)
    logger.info(f"Running on {sys.version} Python")
    logger.info(runningInfo)
    logger.debug(f"Using database at {Config.DB_NAME} in {Config.DB_FORMAT} format")
    logger.debug(f"{mode}")

    flag = (True if duplicateFile else False)  # If no duplicateFile then print to screen.
    License.printShortLicense(Config.NAME, Config.VERSION, duplicateFile, flag)

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    if zap:
        if Config.ZAP_RECYCLE:
            logger.debug("Will zap [Recycle mode] none music files.")
        else:
            logger.debug("Will zap [Delete mode] none music files.")

    fileList = []
    songsCount = duplicateUtils.countSongs(sourceDir, fileList, Config.NCOLS)

    if build:
        duplicateUtils.logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds.  {mode}", duplicateFile, logger)
        duplicateUtils.logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile, logger)
        scanMusic("build", fileList, duplicateFile, difference, songsCount, noPrint, checkThe, Config.SOUNDEX, Config.TAGS)
    else:
        duplicateUtils.logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds  {mode}", duplicateFile, logger)
        duplicateUtils.logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile, logger)
        scanMusic("scan", fileList, duplicateFile, difference, songsCount, noPrint, checkThe, Config.SOUNDEX, Config.TAGS)

    if noSave:
        logger.debug("Not Saving database")
    else:
        if not Config.DB_OVERWRITE:
            logger.debug(f"Not over writing database {DBpath}")
        songLibrary.DBOverWrite(Config.DB_OVERWRITE)
        songLibrary.save()

    timeStop = timer.Stop

    message = f"{Config.NAME} Completed :: {timeStop}"

    duplicateUtils.logTextLine("", duplicateFile)
    duplicateUtils.logTextLine(message, duplicateFile)
    duplicateUtils.logTextLine("", duplicateFile)
    print(message)

    #logger.info(f"{removeThe.cache_info()}")
    logger.info(message)
    logger.info(f"End of {Config.NAME} {Config.VERSION}")

    if Config.NOTIFICATION: notification.notify(Config.NAME, message, Config.NAME, icon, timeout)

    sys.exit(0)
