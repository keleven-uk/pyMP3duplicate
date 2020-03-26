###############################################################################################################
#  pyMP3duplicate                                                                                             #
#                                                                                                             #
#  The program will scan a given directory and report duplicate MP3 files.                                    #
#                                                                                                             #
# usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-d DIFFERANCE] [-xL] [-xS] [-b] [-n] [-l] [-v]   #
#                                                                                                             #
#       Kevin Scott     2020                                                                                  #
#                                                                                                             #
#   For changes see history.txt                                                                               #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2019 - 2020>  <Kevin Scott>                                                               #
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
import pathlib
import textwrap
import datetime
import argparse
import colorama
import myConfig
import myLogger
import myLibrary
from tqdm import tqdm
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from tinytag import TinyTag
from myLicense import printLongLicense, printShortLicense, logTextLine

####################################################################################### checkToIgnore ##############
def checkToIgnore(musicDuplicate, songDuplicate):
    """  Each song may carry a ignore flag, return True if these are same.
         Only checked it tag are read using mutagen.
    """
    if (musicDuplicate == myConfig.IGNORE()) and (songDuplicate == myConfig.IGNORE()):
        return True
    else:
        return False
####################################################################################### scanTags ##############
def scanTags(musicFile):
    """  Scans the musicfile for the required tags.
         Will use the method indicated in the user config.
    """
    if myConfig.TAGS() == "tinytag":
        tags      = TinyTag.get(musicFile)
        key       = f"{tags.artist}:{tags.title}"
        duration  = tags.duration
        duplicate = ""
    elif myConfig.TAGS() == "eyed3":
        tags      = eyed3.load(musicFile)
        key       = f"{tags.tag.artist}:{tags.tag.title}"
        duration  = tags.info.time_secs
        duplicate = ""
    elif myConfig.TAGS() == "mutagen":
        tags     = ID3(musicFile)
        audio    = MP3(musicFile)
        artist   = tags["TPE1"][0]
        title    = tags["TIT2"][0]
        key      = f"{artist}:{title}"
        duration = audio.info.length
        try:
            duplicate = tags["TXXX:DUPLICATE"][0]
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

    return key, musicDuration, duplicate

####################################################################################### countSongs ############
def countSongs(sourceDir):
    """  Count the number of songs [.mp3 files] in the sourceDir.
         This count is used in the progress bat in scanMusic()
         Takes just over a second at 130000 files approx.
    """
    print("Counting Songs")
    count = 0
    for musicFile in tqdm(sourceDir.glob("**/*.mp3"), unit="songs", ncols=myConfig.NCOLS(), position=0):
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
    count      = 0
    duplicates = 0
    nonMusic   = 0
    ignored    = 0
    ignoreSong = myConfig.IGNORE()

    for musicFile in tqdm(sourceDir.glob("**/*.*"), total=songsCount, unit="songs", ncols=myConfig.NCOLS(), position=1):

        if musicFile.is_dir(): continue     # ignore directories.

        if not str(musicFile).endswith(".mp3"):      # a non music file found.
            if mode == "scan":
                logTextLine("-"*80 + "Non Music File Found" + "-"*30, duplicateFile)
                logTextLine(f"{str(musicFile)} is not a music file", duplicateFile)
                nonMusic += 1
            continue        # continue with next file.

        try:
            count += 1
            key, musicDuration, musicDuplicate = scanTags(musicFile)

            if songLibrary.hasKey(key):
                if mode == "build":  # Only building database - do not check for duplicates.
                    continue

                songFile, songDuration, songDuplicate = songLibrary.getItem(key)

                if abs(musicDuration - songDuration) < difference:
                    if myConfig.TAGS() == "mutagen":  # Using mutagen, we should check for ignore flag
                        if checkToIgnore(musicDuplicate, songDuplicate):
                            ignored += 1
                            continue
                    logTextLine("-"*80 + "Duplicate Found" + "-"*30, duplicateFile)
                    logTextLine(f"{str(musicFile)} {musicDuration:.2f}", duplicateFile)
                    logTextLine(f"{str(songFile)}  {songDuration:.2f}", duplicateFile)
                    duplicates += 1

            else:  # if songLibrary.hasKey(key):
                songLibrary.addItem(key, musicFile, musicDuration, musicDuplicate)

        except (Exception) as error:
            logger.error(f"ERROR : {str(musicFile)} :: {error}", exc_info=True)

    logTextLine("", duplicateFile)
    if nonMusic and ignored:
        logTextLine(f"{count} music files found with {duplicates} duplicates, \
                    with {nonMusic} non music files and {ignored} songs.", duplicateFile)
    elif nonMusic:
        logTextLine(f"{count} music files found with {duplicates} duplicates, \
                    with {nonMusic} non music files.", duplicateFile)
    else:
        logTextLine(f"{count} music files found with {duplicates} duplicates.", duplicateFile)

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
        epilog = f" Kevin Scott (C) 2020 :: {myConfig.NAME()} V{myConfig.VERSION()}")

    parser.add_argument("-s",  "--sourceDir",  type=pathlib.Path, action="store", default=False, help="directory of the music files [mp3].")
    parser.add_argument("-f",  "--dupFile",    type=pathlib.Path, action="store", default=False, help="[Optional] list duplicates to file.")
    parser.add_argument("-d",  "--difference", type=float, action="store", default=0.5, help="Time difference between songs, default = 0.5s.")
    parser.add_argument("-xL", "--noLoad",     action="store_true" , help="Do not load database.")
    parser.add_argument("-xS", "--noSave",     action="store_true" , help="Do not save database.")
    parser.add_argument("-b",  "--build",      action="store_true" , help="Build the database only.")
    parser.add_argument("-n",  "--number",     action="store_true" , help="print the Number of Songs in the database.")
    parser.add_argument("-l",  "--license",    action="store_true" , help="Print the Software License.")
    parser.add_argument("-v",  "--version",    action="store_true" , help="print the version of the application.")

    args = parser.parse_args()

    if args.version:
        printShortLicense(myConfig.NAME(), myConfig.VERSION(), "", False)
        logger.info(f"End of {myConfig.NAME()} V{myConfig.VERSION()}: version")
        exit(0)

    if args.number:
        songLibrary.load()
        l = songLibrary.noOfItems()
        printShortLicense(myConfig.NAME(), myConfig.VERSION(), "", False)
        print(f"Song Library has {l} songs")
        logger.info(f"End of {myConfig.NAME()} V{myConfig.VERSION()} : Song Library has {l} songs")
        exit(0)

    if args.license:
        printLongLicense(myConfig.NAME(), myConfig.VERSION())
        logger.info(f"End of {myConfig.NAME()} V{myConfig.VERSION()} : Printed Licence")
        exit(0)

    if not args.sourceDir or not args.sourceDir.exists():
        logger.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        exit(1)

    if not args.sourceDir or not args.sourceDir.exists():
        logger.error("Source Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Source Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        exit(2)

    return (args.sourceDir, args.dupFile, args.noLoad, args.noSave, args.build, args.difference)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime   = time.time()
    myConfig    = myConfig.Config()
    songLibrary = myLibrary.Library()                             # Create the song library
    logger      = myLogger.get_logger(myConfig.NAME() + ".log")   # Create the logger.

    logger.info("-"*50)
    logger.info(f"Start of {myConfig.NAME()} {myConfig.VERSION()}")
    logger.info(f"Extracting tags using {myConfig.TAGS()}")

    sourceDir, duplicateFile, noLoad, noSave, build, difference = parseArgs()

    printShortLicense(myConfig.NAME(), myConfig.VERSION(), duplicateFile, True)

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    songsCount = countSongs(sourceDir)
    elapsedTimeSecs  = time.time()  - startTime

    if build:
        logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {datetime.timedelta(seconds = elapsedTimeSecs)}", duplicateFile)
        logger.debug(f"Building Database from {sourceDir} with a time difference of {difference} seconds")
        scanMusic("build", sourceDir, duplicateFile, difference, songsCount)
    else:
        logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds", duplicateFile)
        logTextLine(f"... with a song count of {songsCount} in {datetime.timedelta(seconds = elapsedTimeSecs)}", duplicateFile)
        logger.debug(f"Scanning {sourceDir} with a time difference of {difference} seconds")
        scanMusic("scan", sourceDir, duplicateFile, difference, songsCount)

    if noSave:
        logger.debug("Not Saving database")
    else:
        songLibrary.save()

    logTextLine("", duplicateFile)
    elapsedTimeSecs  = time.time()  - startTime
    logTextLine(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)} :: using {myConfig.TAGS()}", duplicateFile)
    logTextLine("", duplicateFile)

    logger.info(f"End of {myConfig.NAME()} {myConfig.VERSION()}")

    exit(0)