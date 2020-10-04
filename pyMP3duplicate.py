###############################################################################################################
#    pyMP3duplicate   Copyright (C) <2020>  <Kevin Scott>                                                     #                                                                                                             #
#    The program will scan a given directory and report duplicate MP3 files.                                  #
#                                                                                                             #
# usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-d DIFFERENCE] [-xL] [-xS] [-b] [-n] [-l] [-v]   #
#                                                                                                             #
#     For changes see history.txt                                                                             #
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
import eyed3
import textwrap
import argparse
import colorama
import myTimer
import myConfig
import myLogger
import myLibrary
from tqdm import tqdm
from pathlib import Path
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from tinytag import TinyTag
from plyer import notification
#from functools import lru_cache
from libindic.soundex import Soundex
from myExceptions import TagReadError
from myLicense import printLongLicense, printShortLicense, logTextLine

####################################################################################### checktags #############
def checktags(musicFile, songFile):
    """  Used to check if the Soundex algorithm has returned a false positive.
         Returns true if the artist and title of the two songs are the same.
    """
    try:                                    # Tries to read tags from the music file.
        tags = TinyTag.get(musicFile)
    except:           # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {musicFile}")
    artist1 = removeThe(tags.artist)
    title1  = removeThe(tags.title)

    try:                                    # Tries to read tags from the music file.
        tags = TinyTag.get(songFile)
    except:           # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {songFile}")
    artist2 = removeThe(tags.artist)
    title2  = removeThe(tags.title)

    return (True if (artist1 == artist2) and (title1 == title2) else False)

####################################################################################### checkToIgnore #########
def checkToIgnore(musicDuplicate, songDuplicate):
    """  Each song may carry a ignore flag, return True if these are the same.
         Only checked if the tags are read using mutagen.
    """
    if (musicDuplicate == myConfig.IGNORE) and (songDuplicate == myConfig.IGNORE):
        return True
    else:
        return False

####################################################################################### createKey #############
def createKey(artist, title):
    """ Creates the key from the artist and title.
        key is either formed from string substitution or created from the soundex of the string.
    """
    return (phonetic.soundex(f"{artist}:{title}") if myConfig.SOUNDEX else f"{artist}:{title}")

####################################################################################### removeThe #############
#@lru_cache()
def removeThe(name):
    """  Removes 'the' from the from the beginning of artist and title if present.
         Mainly a problem with artist, to be honest.
         Name is returned lower case.
    """
    if name:
        n = name.lower()
        return (name[4:] if n.startswith("the") else name)
    else:
        return ""

####################################################################################### scanTags ##############
def scanTags(musicFile):
    """  Scans the musicfile for the required tags.
         Will use the method indicated in the user configure.

         If there is a problem reading the tags, raise an exception.
    """
    if myConfig.TAGS == "tinytag":
        try:                                    # Tries to read tags from the music file.
            tags = TinyTag.get(musicFile)
        except:           # Can't read tags - flag as error.
            raise TagReadError(f"Tinytag error reading tags {musicFile}")
        artist    = removeThe(tags.artist)
        title     = removeThe(tags.title)
        duration  = tags.duration
        duplicate = ""

    elif myConfig.TAGS == "eyed3":
        try:
            tags = eyed3.load(musicFile)
        except:
            logger.error(f"Eyed3 error reading tags {musicFile}")
            raise TagReadError(f"Eyed3 error reading tags {musicFile}")
        artist    = removeThe(tags.tag.artist)
        title     = removeThe(tags.tag.title)
        duration  = tags.info.time_secs
        duplicate = ""

    elif myConfig.TAGS == "mutagen":
        try:
            tags  = ID3(musicFile)
            audio = MP3(musicFile)
        except:
            raise TagReadError(f"Mutagen error reading tags {musicFile}")
        artist   = removeThe(tags["TPE1"][0])
        title    = removeThe(tags["TIT2"][0])
        duration = audio.info.length
        try:                                        # Try to read duplicate tag.
            duplicate = tags["TXXX:DUPLICATE"][0]   # Ignore if not there.
        except:
            duplicate = ""
    else:
        # Should not happen, tinytag should be returned by default.
        logger.error("Unknown use option for Tags Module.")
        print(f"{colorama.Fore.RED}Unknown use option for Tags Module.{colorama.Fore.RESET}")
        exit(4)

    if not duration:     # In case there is no valid duration time on the mp3 file.
        musicDuration = 0
    else:
        musicDuration = round(duration, 2)

    key = createKey(artist, title)
    return key, musicDuration, duplicate, artist, title

####################################################################################### countSongs ############
def countSongs(sourceDir):
    """  Count the number of songs [.mp3 files] in the sourceDir.
         This count is used in the progress bar in scanMusic()
         Takes just over a second at 130000 files approx.
    """
    print("Counting Songs")
    count = 0
    for musicFile in tqdm(sourceDir.glob("**/*.mp3"), unit="songs", ncols=myConfig.NCOLS, position=0):
        count += 1

    print(f"... with a song count of {count}")
    return count

####################################################################################### scanMusic #############
def scanMusic(mode, sourceDir, duplicateFile, difference, songsCount,  noPrint):
    """  Scan the sourceDir, which should contain mp3 files.
         The songs are added to the library using the song artist and title as key.
         If the song already exists in the library, then the two are checked.

         mode = "scan"  -- the sourceDir is scanned and duplicates are reported.
         mode = "build" -- the sourceDir is scanned and the database is built only, duplicates are not checked.

         Uses tqdm - a very cool progress bar for console windows.
    """
    count      = 0      # Number of song files to check.
    duplicates = 0      # Number of duplicate songs.
    noDups     = 0      # Number of duplicate songs that fall outside of the time difference.
    nonMusic   = 0      # Number of non music files.
    ignored    = 0      # Number of duplicate songs that have been marked to ignore.
    falsePos   = 0      # Number of songs that seem to be duplicate, but ain't.

    for musicFile in tqdm(sourceDir.glob("**/*.*"), total=songsCount, unit="songs", ncols=myConfig.NCOLS, position=1):

        if musicFile.is_dir(): continue                                 # ignore directories.

        if (musicFile.suffix != ".mp3"):                                # A non music file found.
            if mode == "build": continue                                # Ignore non .mp3 files if in build mode.
            if musicFile.suffix == ".pickle": continue                  # Ignore database if stored in target directory.
            if musicFile.suffix == ".json"  : continue                  # Ignore database if stored in target directory.
            logTextLine("-"*80 + "Non Music File Found" + "-" * 40, duplicateFile)
            logTextLine(f"{musicFile} is not a music file",  duplicateFile)
            nonMusic += 1
            continue

        key, musicDuration, musicDuplicate, artist, title = scanTags(musicFile)

        if songLibrary.hasKey(key):
            if mode == "build": continue    # Only analyse songs if in scan mode.
                                            # If build mode, skip.

            songFile, songDuration, songDuplicate = songLibrary.getItem(key)

            if abs(musicDuration - songDuration) < difference:
                if myConfig.TAGS == "mutagen":  # Using mutagen, we should check for ignore flag
                    if checkToIgnore(musicDuplicate, songDuplicate):
                        ignored += 1
                        continue        #  Do not print ignore duplicate
                message = " Duplicate Found "
                if myConfig.SOUNDEX and not checktags(musicFile, songFile):
                    falsePos += 1
                    if not noPrint:
                        message = " Possible False Positive "
                    else:
                        continue        #  Do not print Possible False Positives
                logTextLine("-"*70 + message + "-" * 40, duplicateFile)
                logTextLine(f"{musicFile} {timer.formatSeconds(musicDuration)}", duplicateFile)
                logTextLine(f"{songFile}  {timer.formatSeconds(songDuration)}", duplicateFile)
                duplicates += 1
            else:  # if abs(musicDuration - songDuration) < difference:
                noDups += 1

        else:  # if songLibrary.hasKey(key):  Song is a new find, add to database.
            songLibrary.addItem(key, os.fspath(musicFile), musicDuration, musicDuplicate)
            count += 1

    count = count + noDups + duplicates     # Adjust for duplicates found.

    logTextLine("", duplicateFile)
    if mode == "build":
        logTextLine(f"{count} music files found.", duplicateFile)
    elif nonMusic and ignored:
        logTextLine(f"{count} music files found with {duplicates} duplicates, \
                    with {nonMusic} non music files and {ignored} songs.", duplicateFile)
    elif nonMusic:
        logTextLine(f"{count} music files found with {duplicates} duplicates, \
                    with {nonMusic} non music files.", duplicateFile)
    else:
        logTextLine(f"{count} music files found with {duplicates} duplicates.", duplicateFile)

    if noDups:
        logTextLine(f" Found possible {noDups} duplicates, but with a time difference greater then {difference}.", duplicateFile)

    if falsePos:
        if noPrint:
            logTextLine(f" Found possible {falsePos} false positives [not displayed].", duplicateFile)
        else:
            logTextLine(f" Found possible {falsePos} false positives.", duplicateFile)

############################################################################################## parseArgs ######
def parseArgs():
    """  Process the command line arguments.

         Checks the arguments and will exit if not valid.

         Exit code 0 - program has exited normally, after print version, licence or help.
         Exit Code 1 - No source directory supplied.
         Exit code 2 - Source directory does not exist.
         Exit code 3 - Duplicate File Directory Does Not Exist.
    """
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
        A Python MP3 Duplicate finder.
        -----------------------
        The program will scan a given directory and report duplicate MP3 files."""),
        epilog = f" Kevin Scott (C) 2020 :: {myConfig.NAME} {myConfig.VERSION}")

    parser.add_argument("-s",  "--sourceDir",
        type=Path, action="store", default=False, help="directory of the music files [mp3].")
    parser.add_argument("-f",  "--dupFile",
        type=Path, action="store", default=False, help="[Optional] list duplicates to file, start afresh.")
    parser.add_argument("-fA",  "--dupFileAmend",
        type=Path, action="store", default=False, help="[Optional] list duplicates to file, Amend to previous.")
    parser.add_argument("-d",  "--difference",
        type=float, action="store", default=0.5, help="Time difference between songs, default = 0.5s.")
    parser.add_argument("-xL", "--noLoad",         action="store_true" , help="Do not load database.")
    parser.add_argument("-xS", "--noSave",         action="store_true" , help="Do not save database.")
    parser.add_argument("-c",  "--check",          action="store_true" , help="Check database integrity.")
    parser.add_argument("-cD", "--checkDelete",    action="store_true" , help="Check database integrity and delete unwanted.")
    parser.add_argument("-b",  "--build",          action="store_true" , help="Build the database only.")
    parser.add_argument("-n",  "--number",         action="store_true" , help="Print the Number of Songs in the database.")
    parser.add_argument("-l",  "--license",        action="store_true" , help="Print the Software License.")
    parser.add_argument("-v",  "--version",        action="store_true" , help="Print the version of the application.")
    parser.add_argument("-np", "--noPrint",        action="store_true" , help="Do Not Print Possible False Positives.")

    args = parser.parse_args()

    if args.version:
        printShortLicense(myConfig.NAME, myConfig.VERSION, "", False)
        logger.info(f"End of {myConfig.NAME} V{myConfig.VERSION}: version")
        print("Goodbye.")
        exit(0)

    if args.license:
        printLongLicense(myConfig.NAME, myConfig.VERSION)
        logger.info(f"End of {myConfig.NAME} V{myConfig.VERSION} : Printed Licence")
        print("Goodbye.")
        exit(0)

    if not args.sourceDir and not (args.check or args.checkDelete or args.number):
        logger.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(1)

    if args.sourceDir and not args.sourceDir.exists():      # Only check source dir exits if one was entered.
        logger.error("Source Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Source Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(2)

    if args.dupFile and not args.dupFile.parent.exists():      # Only check Duplicate File Directory exits if one was entered.
        logger.error("Duplicate File Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Duplicate File Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(3)

    if args.check:
        check = "test"
    elif args.checkDelete:
        check = "delete"
    else:
        check = ""

    if args.dupFile:                                            # Delete duplicate file if it exists.
        try:
            dfile = args.dupFile
            os.remove(args.dupFile)
        except (IOError, os.error):
            logger.error("Duplication File Does Not Exist.")    # Log error, but don't really care.
    else:                                                       # Amend to previous duplicate file, if it exists.
        dfile = args.dupFileAmend

    return (args.sourceDir, dfile, args.noLoad, args.noSave, args.build, args.difference, args.number, check,  args.noPrint)

################################################################################### printNumberOfSongs() ######
def printNumberOfSongs():
    """  Print the number of songs in the library.
    """
    printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, False)
    l = songLibrary.noOfItems
    print(f"Song Library has {l} songs")
    logger.info(f"End of {myConfig.NAME} V{myConfig.VERSION} : Song Library has {l} songs")
    print("Goodbye.")
    exit(0)

######################################################################################## checkDatabase() ######
def checkDatabase(check):
    """  Perform a data integrity check on the library.

          if check == test then just report errors.
          if check == delete then report errors and delete entries.
    """
    message = "Running Database Integrity Check"
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, False)
    logger.info(message)
    songLibrary.check(check)
    print("Goodbye.")
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, "Database Check Ended", myConfig.NAME, icon, timeout)
    exit(3)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime   = time.time()

    icon    = "tea.icon"    #  icon used by notifications
    timeout = 5             #  timeout used by notifications in seconds

    myConfig    = myConfig.Config()                                     # Need to do this first.

    DBpath = Path(myConfig.DB_LOCATION + myConfig.DB_NAME)

    songLibrary = myLibrary.Library(DBpath, myConfig.DB_FORMAT)         # Create the song library.
    logger      = myLogger.get_logger(myConfig.NAME + ".log")           # Create the logger.
    timer       = myTimer.Timer()
    phonetic    = Soundex()

    timer.Start

    if myConfig.SOUNDEX:
        mode = f"Using Soundex for {myConfig.TAGS} matching"
    else:
        mode = f"Using Strings for {myConfig.TAGS} matching"

    message = f"Start of {myConfig.NAME} {myConfig.VERSION}"
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    logger.info("-"*100)
    logger.info(message)
    logger.debug(f"Using database at {myConfig.DB_NAME} in {myConfig.DB_FORMAT} format")
    logger.debug(f"{mode}")

    sourceDir, duplicateFile, noLoad, noSave, build, difference, number, check, noPrint = parseArgs()

    if number: printNumberOfSongs()       # Print on number of songs in library.
    if check:  checkDatabase(check)       # Run data integrity check on library.

    flag = (True if duplicateFile else False)   # If no duplicateFile then print to screen.
    printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, flag)

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    songsCount = countSongs(sourceDir)

    if build:
        logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds.  {mode}", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile)
        logger.debug(f"Building Database from {sourceDir} with a time difference of {difference} seconds")
        logger.debug(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds")
        scanMusic("build", sourceDir, duplicateFile, difference, songsCount, noPrint)
    else:
        logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds  {mode}", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile)
        logger.debug(f"Scanning {sourceDir} with a time difference of {difference} seconds")
        logger.debug(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds")
        scanMusic("scan", sourceDir, duplicateFile, difference, songsCount, noPrint)

    if noSave:
        logger.debug("Not Saving database")
    else:
        if not myConfig.DB_OVERWRITE:
            logger.debug(f"Not over writing database {DBpath}")
        songLibrary.DBOverWrite(myConfig.DB_OVERWRITE)
        songLibrary.save()

    timeStop = timer.Stop

    message = f"{myConfig.NAME} Completed :: {timeStop}"

    logTextLine("", duplicateFile)
    logTextLine(message, duplicateFile)
    logTextLine("", duplicateFile)

    #logger.info(f"{removeThe.cache_info()}")
    logger.info(message)
    logger.info(f"End of {myConfig.NAME} {myConfig.VERSION}")

    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    exit(0)
