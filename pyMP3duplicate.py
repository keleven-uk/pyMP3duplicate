###############################################################################################################
#    pyMP3duplicate   Copyright (C) <2020>  <Kevin Scott>                                                     #
#                                                                                                             #
#    The program will scan a given directory and report duplicate MP3 files.                                  #
#                                                                                                             #
# usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-d DIFFERANCE] [-xL] [-xS] [-b] [-n] [-l] [-v]   #
#                                                                                                             #
#     For changes see history.txt                                                                             #
#                                                                                                             #
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
import sys
import time
import eyed3
import textwrap
import datetime
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
    except (Exception) as error:           # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {musicFile}")
    artist1 = removeThe(tags.artist)
    title1  = removeThe(tags.title)

    try:                                    # Tries to read tags from the music file.
        tags = TinyTag.get(songFile)
    except (Exception) as error:           # Can't read tags - log as error.
        logger.error(f"ERROR : Can't read tags : {songFile}")
    artist2 = removeThe(tags.artist)
    title2  = removeThe(tags.title)

    return (True if (artist1 == artist2) and (title1 == title2) else False)

####################################################################################### checkToIgnore #########
def checkToIgnore(musicDuplicate, songDuplicate):
    """  Each song may carry a ignore flag, return True if these are same.
         Only checked it tag are read using mutagen.
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
def removeThe(name):
    """  Removes 'the' from the from the beginning of artist and title if present.
         Mainly a problem with artist, to be honest.
         name is returned lower case.
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
        except (Exception) as error:           # Can't read tags - flag as error.
            raise TagReadError(f"Tinytag error reading tags {musicFile}")
        artist    = removeThe(tags.artist)
        title     = removeThe(tags.title)
        duration  = tags.duration
        duplicate = ""

    elif myConfig.TAGS == "eyed3":
        try:
            tags = eyed3.load(musicFile)
        except (Exception) as error:
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
        except (Exception) as error:
            raise TagReadError(f"Mutagen error reading tags {musicFile}")
        artist   = removeThe(tags["TPE1"][0])
        title    = removeThe(tags["TIT2"][0])
        duration = audio.info.length
        try:                                        # Try to read duplicate tag.
            duplicate = tags["TXXX:DUPLICATE"][0]   # Ignore if not there.
        except (Exception) as error:
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
def scanMusic(mode, sourceDir, duplicateFile, difference, songsCount):
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
    ignoreSong = myConfig.IGNORE

    for musicFile in tqdm(sourceDir.glob("**/*.*"), total=songsCount, unit="songs", ncols=myConfig.NCOLS, position=1):

        if musicFile.is_dir(): continue     # ignore directories.

        if not musicFile.suffix == ".mp3":                 # A non music file found.
            if musicFile.suffix == ".pickle": continue     # Ignore database if stored in target directory.
            if musicFile.suffix == ".json"  : continue     # Ignore database if stored in target directory.
            if mode == "scan":
                logTextLine("-"*80 + "Non Music File Found" + "-"*40, duplicateFile)
                logTextLine(f"{musicFile} is not a music file",  duplicateFile)
                nonMusic += 1
            continue        # continue with next file.

        key, musicDuration, musicDuplicate, artist, title = scanTags(musicFile)

        if songLibrary.hasKey(key):
            if mode == "scan":   # Only analysis songs if scan mode.
                                 # If build mode, skip.

                songFile, songDuration, songDuplicate = songLibrary.getItem(key)

                if abs(musicDuration - songDuration) < difference:
                    if myConfig.TAGS == "mutagen":  # Using mutagen, we should check for ignore flag
                        if checkToIgnore(musicDuplicate, songDuplicate):
                            ignored += 1
                            continue
                    logTextLine("-"*80 + "Duplicate Found" + "-"*40, duplicateFile)
                    if myConfig.SOUNDEX and not checktags(musicFile, songFile):
                        logTextLine("*"*80 + "Possible False Positive" + "*"*32, duplicateFile)
                        falsePos += 1
                    logTextLine(f"{musicFile} {musicDuration:.2f}", duplicateFile)
                    logTextLine(f"{songFile}  {songDuration:.2f}", duplicateFile)
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
        logTextLine(f" Found possible {falsePos} false positives.", duplicateFile)

############################################################################################## parseArgs ######
def parseArgs():
    """  Process the command line arguments.

         Checks the arguments and will exit if not valid.

         Exit code 0 - program has exited normally, after print version, licence or help.
         Exit Code 1 - No source directory supplied.
         Exit code 2 - Source directory does not exist.
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
    parser.add_argument("-cD",  "--checkDelete",   action="store_true" , help="Check database integrity and delete unwanted.")
    parser.add_argument("-b",  "--build",          action="store_true" , help="Build the database only.")
    parser.add_argument("-n",  "--number",         action="store_true" , help="Print the Number of Songs in the database.")
    parser.add_argument("-l",  "--license",        action="store_true" , help="Print the Software License.")
    parser.add_argument("-v",  "--version",        action="store_true" , help="print the version of the application.")

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
        except (IOError, os.error) as error:
            logger.error("Duplication File Does Not Exist.")    # Log error, but don't really care.
    else:                                                       # Amend to previous duplicate file, if it exists.
        dfile = args.dupFileAmend

    return (args.sourceDir, dfile, args.noLoad, args.noSave, args.build, args.difference, args.number, check)

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
    printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, False)
    logger.info("Running database integrity check")
    songLibrary.check(check)
    print("Goodbye.")
    exit(3)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime   = time.time()
    myConfig    = myConfig.Config()                                                # Need to do this first.
    songLibrary = myLibrary.Library(Path(myConfig.DB_NAME), myConfig.DB_FORMAT)    # Create the song library
    logger      = myLogger.get_logger(myConfig.NAME + ".log")                      # Create the logger.
    timer       = myTimer.Timer()
    phonetic    = Soundex()

    timer.Start

    logger.info("-"*100)
    logger.info(f"Start of {myConfig.NAME} {myConfig.VERSION}")
    logger.debug(f"Storing database at {myConfig.DB_NAME} in {myConfig.DB_FORMAT} format")

    sourceDir, duplicateFile, noLoad, noSave, build, difference, number, check = parseArgs()

    if number: printNumberOfSongs()       # Print on number of songs in library.
    if check:  checkDatabase(check)       # Run data integrity check on library.

    flag = (True if duplicateFile else False)   # If no duplicateFile then print to screen.
    printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, flag)

    if myConfig.SOUNDEX:
        logger.debug(f"Using Soundex for {myConfig.TAGS} matching")
        mode = f"Using Soundex for {myConfig.TAGS} matching"
    else:
        logger.debug(f"Using Strings for {myConfig.TAGS} matching")
        mode = f"Using Strings for {myConfig.TAGS} matching"

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    songsCount = countSongs(sourceDir)

    if build:
        logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds.  {mode}", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds",   duplicateFile)
        logger.debug(f"Building Database from {sourceDir} with a time difference of {difference} seconds")
        scanMusic("build", sourceDir, duplicateFile, difference, songsCount)
    else:
        logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds  {mode}", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile)
        logger.debug(f"Scanning {sourceDir} with a time difference of {difference} seconds")
        scanMusic("scan", sourceDir, duplicateFile, difference, songsCount)

    if noSave:
        logger.debug("Not Saving database")
    else:
        songLibrary.save()

    logTextLine("", duplicateFile)
    logTextLine(f"Completed  :: {timer.Stop} Seconds", duplicateFile)
    logTextLine("", duplicateFile)

    logger.info(f"End of {myConfig.NAME} {myConfig.VERSION}")

    exit(0)