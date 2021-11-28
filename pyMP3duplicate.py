###############################################################################################################
#    pyMP3duplicate   Copyright (C) <2020-2021>  <Kevin Scott>                                                #                                                                                                             #                                                                                                             #
#    The program will scan a given directory and report duplicate MP3 files.                                  #
#                                                                                                             #
#  Usage:                                                                                                     #
# pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-fA DUPFILEAMEND] [-d DIFFERENCE] [-b] [-n] [-l]        #
#                                                              [-v] [-e] [-c] [-cD] [-xL] [-xS] [-np] [-zD]   #
#                                                                                                             #
#     For changes see history.txt                                                                             #
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
import sys
import time
import eyed3
import shutil
import textwrap
import argparse
import colorama
from tqdm import tqdm
from pathlib import Path
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from tinytag import TinyTag
from plyer import notification
#from functools import lru_cache
from alive_progress import alive_bar

import src.myTimer as myTimer
import src.myConfig as myConfig
import src.myLogger as myLogger
import src.myLibrary as myLibrary
import src.myLicense as myLicense
import src.myExceptions as myExceptions
import src.utils.zapUtils as zapUtils
import src.utils.duplicateUtils as duplicateUtils


try:
    import pyjion
    pyjion.enable()
except:
    pass

####################################################################################### checktags #############
def checktags(musicFile, songFile):
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

####################################################################################### checkToIgnore #########
def checkToIgnore(musicDuplicate, songDuplicate):
    """  Each song may carry a ignore flag, return True if these are the same.
         Only checked if the tags are read using mutagen.
    """
    if (musicDuplicate == myConfig.IGNORE) and (songDuplicate == myConfig.IGNORE):
        return True
    else:
        return False

####################################################################################### scanTags ##############
def scanTags(musicFile):
    """  Scans the musicfile for the required tags.
         Will use the method indicated in the user configure.

         If there is a problem reading the tags, raise an exception.
    """
    match myConfig.TAGS:
        case "tinytag":
            try:  # Tries to read tags from the music file.
                tags = TinyTag.get(musicFile)
            except Exception as e:  # Can't read tags - flag as error.
                logger.error(f"Tinytag error reading tags :: {e} ")
                raise myExceptions.TagReadError(f"Tinytag error reading tags {musicFile}")
            artist    = duplicateUtils.removeThe(tags.artist)
            title     = duplicateUtils.removeThe(tags.title)
            duration  = tags.duration
            duplicate = ""

        case "eyed3":
            try:
                tags = eyed3.load(musicFile)
            except Exception as e:
                logger.error(f"Eyed3 error reading tags :: {musicFile}")
                raise myExceptions.TagReadError(f"Eyed3 error reading tags {musicFile}")
            artist    = duplicateUtils.removeThe(tags.tag.artist)
            title     = duplicateUtils.removeThe(tags.tag.title)
            duration  = tags.info.time_secs
            duplicate = ""

        case "mutagen":
            try:
                tags  = ID3(musicFile)
                audio = MP3(musicFile)
            except Exception as e:
                logger.error(f"Nutagen error reading tags :: {e} ")
                raise myExceptions.TagReadError(f"Mutagen error reading tags {musicFile}")
            artist   = duplicateUtils.removeThe(tags["TPE1"][0])
            title    = duplicateUtils.emoveThe(tags["TIT2"][0])
            duration = audio.info.length
            try:  # Try to read duplicate tag.
                duplicate = tags["TXXX:DUPLICATE"][0]  # Ignore if not there.
            except Exception as e:
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

    key = duplicateUtils.createKey(artist, title, myConfig.SOUNDEX)
    return key, musicDuration, duplicate, artist, title

####################################################################################### countSongs ############
def countSongs(sourceDir, fileList):
    """  Count the number of songs [.mp3 files] in the sourceDir.
         The filename are save in a list fileList, this is then passed to scanMusic.
         Takes just over a second at 160000 files approx.
    """
    count = 0

    print("Counting Songs")
    for musicFile in tqdm(sourceDir.glob("**/*.mp3"), unit="songs", ncols=myConfig.NCOLS, position=1):
        fileList.append(musicFile)

    print(f"... with a song count of {len(fileList)}")
    return len(fileList)

####################################################################################### scanMusic #############
def scanMusic(mode, fileList, duplicateFile, difference, songsCount, noPrint, checkThe):
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
                key, musicDuration, musicDuplicate, artist, title = scanTags(musicFile)
            except Exception as e:  # Can't read tags - flag as error.
                logger.error(f"Raised exception at calling scanTags :: {e} ")
                continue

            if checkThe and duplicateUtils.trailingThe(artist):
                myLicense.logTextLine("-" * 70 + " Trailing the found " + "-" * 40, duplicateFile)
                myLicense.logTextLine(f"{artist} is wrong in {musicFile}.", duplicateFile)
                noTrailing +=1

            if songLibrary.hasKey(key):
                if mode == "build": continue  # Only analyse songs if in scan mode.

                songFile, songDuration, songDuplicate = songLibrary.getItem(key)

                if abs(musicDuration - songDuration) < difference:
                    if myConfig.TAGS == "mutagen":  # Using mutagen, we should check for ignore flag
                        if checkToIgnore(musicDuplicate, songDuplicate):
                            ignored += 1
                            continue  # Do not print ignore duplicate
                    message = " Duplicate Found "
                    if myConfig.SOUNDEX and not checktags(musicFile, songFile):
                        falsePos += 1
                        if not noPrint:
                            message = " Possible False Positive "
                        else:
                            continue  # Do not print Possible False Positives
                    myLicense.logTextLine("-" * 70 + message + "-" * 40, duplicateFile)
                    myLicense.logTextLine(f"{musicFile} {timer.formatSeconds(musicDuration)}", duplicateFile)
                    myLicense.logTextLine(f"{songFile}  {timer.formatSeconds(songDuration)}", duplicateFile)
                    duplicates += 1
                else:  # if abs(musicDuration - songDuration) < difference:
                    noDups += 1

            else:  # if songLibrary.hasKey(key):  Song is a new find, add to database.
                songLibrary.addItem(key, os.fspath(musicFile), musicDuration, musicDuplicate)

            bar()   #  Update alive_bar.

    count = songLibrary.noOfItems + noDups + duplicates  # Adjust for duplicates found.

    myLicense.logTextLine("", duplicateFile)
    if mode == "build":
        myLicense.logTextLine(f"{count} music files found.", duplicateFile)
    elif ignored:
        myLicense.logTextLine(f"{count} music files found with {duplicates} duplicates, with {ignored} songs.", duplicateFile)
    else:
        myLicense.logTextLine(f"{count} music files found with {duplicates} duplicates.", duplicateFile)

    if noDups:
        myLicense.logTextLine(f" Found possible {noDups} duplicates, but with a time difference greater then {difference}.", duplicateFile)

    if noTrailing:
        myLicense.logTextLine(f" Found possible {noTrailing} artists with a trailing 'the' in their name.", duplicateFile)

    if falsePos:
        if noPrint:
            myLicense.logTextLine(f" Found possible {falsePos} false positives [not displayed].", duplicateFile)
        else:
            myLicense.logTextLine(f" Found possible {falsePos} false positives.", duplicateFile)

######################################################################################## checkDatabase() ######
def checkDatabase(check, dfile):
    """  Perform a data integrity check on the library.

          if check == test then just report errors.
          if check == delete then report errors and delete entries.
    """
    message = "Running Database Integrity Check"
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    myLicense.printShortLicense(myConfig.NAME, myConfig.VERSION, dfile, False)
    logger.info(message)
    songLibrary.check(check)
    print("Goodbye.")
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, "Database Check Ended", myConfig.NAME, icon, timeout)
    exit(3)

############################################################################################## parseArgs ######
def parseArgs():
    """  Process the command line arguments.

         Checks the arguments and will exit if not valid.

         Exit code 0 - program has exited normally, after print version, licence or help.
         Exit code 0 - Program has exited normally, after Loading program working directory into file explorer.
         Exit Code 1 - No source directory supplied.
         Exit code 2 - Source directory does not exist.
         Exit code 3 - Duplicate File Directory Does Not Exist.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
        A Python MP3 Duplicate finder.
        -----------------------
        The program will scan a given directory and report duplicate MP3 files."""),
        epilog=f" Kevin Scott (C) 2020-2021 :: {myConfig.NAME} {myConfig.VERSION}")

    parser.add_argument("-s", "--sourceDir", type=Path, action="store", help="directory of the music files [mp3].")
    parser.add_argument("-f", "--dupFile", type=Path, action="store", default=False,
                        help="[Optional] list duplicates to file, start afresh.")
    parser.add_argument("-fA", "--dupFileAmend", type=Path, action="store", default=False,
                        help="[Optional] list duplicates to file, Amend to previous.")
    parser.add_argument("-d", "--difference",
                        type=float, action="store", default=0.5, help="Time difference between songs, default = 0.5s.")
    parser.add_argument("-b", "--build", action="store_true", help="Build the database only.")
    parser.add_argument("-n", "--number", action="store_true", help="Print the Number of Songs in the database.")
    parser.add_argument("-l", "--license", action="store_true", help="Print the Software License.")
    parser.add_argument("-v", "--version", action="store_true", help="Print the version of the application.")
    parser.add_argument("-e", "--explorer", action="store_true", help="Load program working directory into file explorer.")
    parser.add_argument("-t", "--checkThe", action="store_true", help="Check for a artist for trailing ',the'.")
    parser.add_argument("-c", "--check", action="store_true", help="Check database integrity.")
    parser.add_argument("-cD", "--checkDelete", action="store_true", help="Check database integrity and delete unwanted.")
    parser.add_argument("-xL", "--noLoad", action="store_true", help="Do not load database.")
    parser.add_argument("-xS", "--noSave", action="store_true", help="Do not save database.")
    parser.add_argument("-np", "--noPrint", action="store_true", help="Do Not Print Possible False Positives.")
    parser.add_argument("-zD", "--zapNoneMusic", action="store_true", help="Zap [DELETE] none music files.")

    args = parser.parse_args()

    if args.version:
        myLicense.printShortLicense(myConfig.NAME, myConfig.VERSION, "", False)
        print(f"Running on {sys.version} Python")
        logger.info(f"Running on {sys.version} Python")
        logger.info(f"End of {myConfig.NAME} V{myConfig.VERSION}: version")
        print("Goodbye.")
        exit(0)

    if args.license:
        myLicense.printLongLicense(myConfig.NAME, myConfig.VERSION)
        logger.info(f"End of {myConfig.NAME} V{myConfig.VERSION} : Printed Licence")
        print("Goodbye.")
        exit(0)

    if not args.sourceDir and not (args.check or args.checkDelete or args.number or args.explorer):
        logger.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(1)

    if args.sourceDir and not args.sourceDir.exists():  # Only check source dir exits if one was entered.
        logger.error("Source Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Source Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(2)

    if args.dupFile and not args.dupFile.parent.exists():  # Only check Duplicate File Directory exits if one was entered.
        logger.error("Duplicate File Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Duplicate File Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        exit(3)

    if args.dupFile:  # Delete duplicate file if it exists.
        try:
            dfile = args.dupFile
            os.remove(args.dupFile)
        except (IOError, os.error):
            logger.error("Duplication File Does Not Exist.")  # Log error, but don't really care.
    else:  # Amend to previous duplicate file, if it exists.
        dfile = args.dupFileAmend

    if args.number :
        myLicense.printShortLicense(myConfig.NAME, myConfig.VERSION, dfile, False)
        l = songLibrary.noOfItems
        print(f"Song Library has {l} songs")                 # Print on number of songs in library.
        print("Goodbye.")
        exit(0)

    if args.check:
        check = "test"
        checkDatabase("test", dfile)                    # Run data integrity check in test mode on library.
    elif args.checkDelete:
        checkDatabase("delete", dfile)                  # Run data integrity check in delete mode on library.

    if args.explorer:
        duplicateUtils.loadExplorer(logger)             # Load program working directory n file explorer.
        print("Goodbye.")
        exit(0)

    return (args.sourceDir, dfile, args.noLoad, args.noSave, args.build, args.difference, args.noPrint, args.zapNoneMusic, args.checkThe)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime = time.time()

    icon    = "resources\\tea.ico"  # icon used by notifications
    timeout = 5  # timeout used by notifications in seconds

    myConfig = myConfig.Config()  # Need to do this first.

    DBpath = Path("data", myConfig.DB_LOCATION + myConfig.DB_NAME)
    LGpath = "data\\" +myConfig.NAME +".log"                     #  Must be a string for a logger path.

    songLibrary = myLibrary.Library(DBpath, myConfig.DB_FORMAT)  # Create the song library.
    logger      = myLogger.get_logger(LGpath)                    # Create the logger.
    timer       = myTimer.Timer()

    sourceDir, duplicateFile, noLoad, noSave, build, difference, noPrint, zap, checkThe = parseArgs()

    timer.Start

    if myConfig.SOUNDEX:
        mode = f"Using Soundex for {myConfig.TAGS} matching"
    else:
        mode = f"Using Strings for {myConfig.TAGS} matching"

    message = f"Start of {myConfig.NAME} {myConfig.VERSION}"
    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    logger.info("-" * 100)
    logger.info(message)
    logger.debug(f"Using database at {myConfig.DB_NAME} in {myConfig.DB_FORMAT} format")
    logger.debug(f"{mode}")

    flag = (True if duplicateFile else False)  # If no duplicateFile then print to screen.
    myLicense.printShortLicense(myConfig.NAME, myConfig.VERSION, duplicateFile, flag)

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    if zap:
        if myConfig.ZAP_RECYCLE:
            logger.debug("Will zap [Recycle mode] none music files.")
        else:
            logger.debug("Will zap [Delete mode] none music files.")

    fileList = []
    songsCount = countSongs(sourceDir, fileList)

    if build:
        myLicense.logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds.  {mode}",
                    duplicateFile)
        myLicense.logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile)
        logger.debug(f"Building Database from {sourceDir} with a time difference of {difference} seconds")
        logger.debug(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds")
        scanMusic("build", fileList, duplicateFile, difference, songsCount, noPrint, checkThe)
    else:
        myLicense.logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds  {mode}", duplicateFile)
        myLicense.logTextLine(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds", duplicateFile)
        logger.debug(f"Scanning {sourceDir} with a time difference of {difference} seconds")
        logger.debug(f"... with a song count of {songsCount} in {timer.Elapsed} Seconds")
        scanMusic("scan", fileList, duplicateFile, difference, songsCount, noPrint, checkThe)
        zapUtils.removeUnwanted(sourceDir, duplicateFile, myConfig.EMPTY_DIR, zap, myConfig.ZAP_RECYCLE, logger)


    if noSave:
        logger.debug("Not Saving database")
    else:
        if not myConfig.DB_OVERWRITE:
            logger.debug(f"Not over writing database {DBpath}")
        songLibrary.DBOverWrite(myConfig.DB_OVERWRITE)
        songLibrary.save()

    timeStop = timer.Stop

    message = f"{myConfig.NAME} Completed :: {timeStop}"

    myLicense.logTextLine("", duplicateFile)
    myLicense.logTextLine(message, duplicateFile)
    myLicense.logTextLine("", duplicateFile)
    print(message)

    #logger.info(f"{removeThe.cache_info()}")
    logger.info(message)
    logger.info(f"End of {myConfig.NAME} {myConfig.VERSION}")

    if myConfig.NOTIFICATION: notification.notify(myConfig.NAME, message, myConfig.NAME, icon, timeout)
    exit(0)
