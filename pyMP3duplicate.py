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
import time
import pathlib
import textwrap
import datetime
import argparse
import colorama
import myLibrary
import myConfig
import myLogger

from tinytag import TinyTag
from myLicense import printLongLicense, printShortLicense, logTextLine

####################################################################################### scanMusic #############
def scanMusic(mode, sourceDir, duplicateFile, difference):
    """  Scan the sourceDir, which should contain mp3 files.
         The songs are added to the library using the song artist and title as key.
         If the song already exists in the library, then the two are checked.

         mode = "scan"  -- the sourceDir is scanned and duplicates are reported.
         mode = "build" -- the sourceDir is scanned and the database is built only, duplicates are not checked.
    """
    startTime  = time.time()
    count      = 0
    duplicates = 0
    nonMusic   = 0

    # Using os.walk seems faster but only just slightly.
    # But gives extra functionality, non music files can be flagged
    #for musicFile in sourceDir.glob("**/*.mp3"):
    for root, dirs, files in os.walk(sourceDir):
        for file in files:
            musicFile = os.path.join(root, file)
            if not musicFile.endswith(".mp3"):      # a non music file found.
                if mode == "scan":
                    logTextLine("-"*80 + "Non Music File Found" + "-"*25, duplicateFile)
                    logTextLine(f"{musicFile} is not a music file", duplicateFile)
                    nonMusic += 1
                continue        # continue with next file.

            try:
                count += 1
                tag = TinyTag.get(musicFile)
                key = f"{tag.artist}:{tag.title}"
                if not tag.duration:     # In case there is no valid duration time on the mp3 file.
                    musicDuration = 0
                else:
                    musicDuration = round(tag.duration, 2)

                if songLibrary.hasKey(key):
                    if mode == "build":  # Only building database - do not check for duplicates.
                        continue

                    songFile, songDuration = songLibrary.getItem(key)
                    if not songDuration: songDuration = 0     # In case there is no valid duration time on the mp3 file.

                    if abs(musicDuration - songDuration) < difference:
                        logTextLine("-"*80 + "Duplicate Found" + "-"*30, duplicateFile)
                        logTextLine(f"{str(musicFile)} {musicDuration:.2f}", duplicateFile)
                        logTextLine(f"{str(songFile)}  {songDuration:.2f}", duplicateFile)
                        duplicates += 1
                else:  # if songLibrary.hasKey(key):
                    songLibrary.addItem(key, musicFile, musicDuration)

            except (Exception) as error:
                logger.error(f"ERROR : {str(musicFile)} :: {error}", exc_info=True)

            if (count % myConfig.ITERATIONS()) == 0:
                elapsedTimeSecs = time.time() - startTime
                elapsedTime     = datetime.timedelta(seconds = elapsedTimeSecs)
                print(f"{count}, duplicates {duplicates}: {elapsedTime} :: {count/elapsedTimeSecs:.1f} songs per sec.")

    logTextLine("", duplicateFile)
    if nonMusic:
        logTextLine(f"{count} music files found with {duplicates} duplicates, with {nonMusic} non music files.", duplicateFile)
    else:
        logTextLine(f"{count} music files found with {duplicates} duplicates.", duplicateFile)

############################################################################################## parseArgs ######
def parseArgs():
    """  Process the command line arguments.

         Checks the arguments and will exit if not valid.

         Exit code 0 - program has exited normally, after print licence or help.
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
    parser.add_argument("-v",  "--version",    action="version"    , version=f"{myConfig.NAME()} V{myConfig.VERSION()}")

    args = parser.parse_args()

    if args.number:
        songLibrary.load()
        l = songLibrary.noOfItems()
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

    sourceDir, duplicateFile, noLoad, noSave, build, difference = parseArgs()
    printShortLicense(myConfig.NAME(), myConfig.VERSION(), duplicateFile)

    if noLoad or build:
        logger.debug("Not Loading database")
    else:
        songLibrary.load()

    logTextLine("", duplicateFile)
    if build:
        logTextLine(f"Building Database from {sourceDir} with a time difference of {difference} seconds", duplicateFile)
        logger.debug(f"Building Database from {sourceDir} with a time difference of {difference} seconds")
        scanMusic("build", sourceDir, duplicateFile, difference)
    else:
        logTextLine(f"Scanning {sourceDir} with a time difference of {difference} seconds", duplicateFile)
        logger.debug(f"Scanning {sourceDir} with a time difference of {difference} seconds")
        scanMusic("scan", sourceDir, duplicateFile, difference)

    if noSave:
        logger.debug("Not Saving database")
    else:
        songLibrary.save()

    logTextLine("", duplicateFile)
    elapsedTimeSecs  = time.time()  - startTime
    logTextLine(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)}", duplicateFile)
    logTextLine("", duplicateFile)

    logger.info(f"End of {myConfig.NAME()} {myConfig.VERSION()}")

    exit(0)