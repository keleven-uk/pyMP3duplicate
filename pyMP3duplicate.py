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
import pickle
import pathlib
import textwrap
import datetime
import argparse
import colorama
import myLogger
from tinytag import TinyTag
from _version import myVERSION, myNAME

class Library():
    """  A simple class that wraps the library dictionary.
    """

    def __init__(self):
        self.library = {}

    def hasKey(self, key):
        """  Returns true if the key exist in the library.
        """
        return key in self.library

    def addItem(self, key, item1, item2):
        """  Adds to the library at point key, added is a list of items.
             item1 is song duration.
             item2 is song path.
        """
        self.library[key] = [item1, item2]

    def getItem(self, key):
        """  Returns items at position key from the library.
        """
        return self.library[key]

    def noOfItems(self):
        """  Return the number of entries in the library
        """
        return len(self.library)

    def save(self):
        """  Save the library to disc - currently uses pickle.
        """
        with open("dup.pickle", "wb") as f:
            pickle.dump(self.library, f)

    def load(self):
        """  Loads the library from disc - currently uses pickle.
        """
        if os.path.isfile("dup.pickle"):
            with open("dup.pickle", "rb") as f:
                self.library = pickle.load(f)

####################################################################################### buildDataBase #########
def buildDataBase(sourceDir):
    """  Build the database only, does no duplicate checking.
         If an old database exists, it will be over written.
    """
    count = 0
    for musicFile in sourceDir.glob("**/*.mp3"):
        try:
            count += 1
            tag = TinyTag.get(musicFile)
            key = f"{tag.artist}:{tag.title}"
            if not tag.duration:     # In case there is no valid duration time on the mp3 file.
                musicDuration = 0
            else:
                musicDuration = round(tag.duration, 2)

            if songLibrary.hasKey(key):
                songFile, songDuration = songLibrary.getItem(key)

                if not songDuration: songDuration = 0     # In case there is no valid duration time on the mp3 file.

                if abs(musicDuration - songDuration) < differance:
                    log.debug(f"{key} already exists")
            else:  # if abs(musicDuration - songDuration) < difference:
                songLibrary.addItem(key, musicFile, musicDuration)

        except (Exception) as error:
            log.error(f"ERROR : {musicFile} :: {error}", exc_info=True)
            print(f"ERROR : {musicFile}     :: {error}")

        if (count % 10000) == 0:
            elapsedTimeSecs = time.time() - startTime
            print(f"{count}: {datetime.timedelta(seconds = elapsedTimeSecs)}")

    print()
    logTextLine(f"{count} music files found.")
####################################################################################### printDuplicate ########
def logTextLine(textLine):
    """  It the global argument duplcateFile is set, then with the line of text
    to that file, else print to screen.

    textLine needs to a string, for f.write - NOT a path.
    """
    if duplicateFile:
        with open(duplicateFile, encoding='utf-8', mode="a") as f:     # Open in amend mode, important.
            f.write(textLine + "\n")
    else:
        print(textLine)

####################################################################################### scanMusic #############
def scanMusic(sourceDir, duplicateFile, differance):
    """  Scan the sourceDir, which should contain mp3 files.
         The songs are added to the library using the song artist and title as key.
         If the song already exists in the library, then to two are checked.
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
                logTextLine("-"*80 + "Non Music File Found" + "-"*25)
                logTextLine(f"{musicFile} is not a music file")
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
                    songFile, songDuration = songLibrary.getItem(key)
                    if not songDuration: songDuration = 0     # In case there is no valid duration time on the mp3 file.

                    if abs(musicDuration - songDuration) < differance:
                        logTextLine("-"*80 + "Duplicate Found" + "-"*30)
                        logTextLine(f"{str(musicFile)} {musicDuration:.2f}")
                        logTextLine(f"{str(songFile)}  {songDuration:.2f}")
                        duplicates += 1
                else:  # if abs(musicDuration - songDuration) < difference:
                    songLibrary.addItem(key, musicFile, musicDuration)

            except (Exception) as error:
                log.error(f"ERROR : {str(musicFile)} :: {error}", exc_info=True)
                print(f"ERROR : {str(musicFile)} :: {error}")

            if (count % 10000) == 0:
                elapsedTimeSecs = time.time() - startTime
                print(f"{count}, duplicates {duplicates}: {datetime.timedelta(seconds = elapsedTimeSecs)}")

    logTextLine("")
    if nonMusic:
        logTextLine(f"{count} music files found with {duplicates} duplicates, with {nonMusic} non music files.")
    else:
        logTextLine(f"{count} music files found with {duplicates} duplicates.")

########################################################################################### printSortLicense ######
def printShortLicense():
    logTextLine("")
    logTextLine(f"{myNAME} V{myVERSION}   Copyright (C) 2020  Kevin Scott")
    logTextLine(f"This program comes with ABSOLUTELY NO WARRANTY; for details type `{myNAME} -l'.")
    logTextLine("This is free software, and you are welcome to redistribute it under certain conditions.")

########################################################################################### printLongLicense ######
def printLongLicense():
    print(f"""
    {myNAME} V{myVERSION}   Copyright (C) 2020  Kevin Scott

    This program is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either myVERSION 3 of the License, or
    (at your option) any later myVERSION.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """, end="")

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
        epilog = f" Kevin Scott (C) 2020 :: {myNAME} V{myVERSION}")

    parser.add_argument("-s",  "--sourceDir",  type=pathlib.Path, action="store", default=False, help="directory of the music files [mp3].")
    parser.add_argument("-f",  "--dupFile",    type=pathlib.Path, action="store", default=False, help="[Optional] list duplicates to file.")
    parser.add_argument("-d",  "--difference", type=float, action="store", default=0.5, help="Time difference between songs, default = 0.5s.")
    parser.add_argument("-xL", "--noLoad",     action="store_true" , help="Do not load database.")
    parser.add_argument("-xS", "--noSave",     action="store_true" , help="Do not save database.")
    parser.add_argument("-b",  "--build",      action="store_true" , help="Build the database only.")
    parser.add_argument("-n",  "--number",     action="store_true" , help="print the Number of Songs in the database.")
    parser.add_argument("-l",  "--license",    action="store_true" , help="Print the Software License.")
    parser.add_argument("-v",  "--version",    action="version"    , version=f"{myNAME} V{myVERSION}")

    args = parser.parse_args()

    if args.number:
        songLibrary.load()
        print("Loaded")
        l = songLibrary.noOfItems()
        print(f"Song Library has {l} songs")
        log.info(f"End of {myNAME} V{myVERSION} : Printed Number of Items {l}")
        exit(0)

    if args.license:
        printLongLicense()
        log.info(f"End of {myNAME} V{myVERSION} : Printed Licence")
        exit(0)

    if not args.sourceDir or not args.sourceDir.exists():
        log.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        exit(1)

    if not args.sourceDir or not args.sourceDir.exists():
        log.error("Source Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Source Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        exit(2)

    return (args.sourceDir, args.dupFile, args.noLoad, args.noSave, args.build, args.differance)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime = time.time()

    songLibrary = Library()             # Create the song library

    log = myLogger.get_logger(myNAME)   # Create the logger.
    log.info("-"*50)
    log.info(f"Start of {myNAME} V{myVERSION}")

    sourceDir, duplicateFile, noLoad, noSave, build, differance = parseArgs()
    printShortLicense()

    if build:
        log.debug("Building database")
        buildDataBase(sourceDir)

    if noLoad or build:
        log.debug("Not Loading database")
    else:
        songLibrary.load()

    logTextLine(f"Scanning {sourceDir} with a time difference of {difference}")

    if not build:
        scanMusic(sourceDir, duplicateFile, differance)

    if noSave:
        log.debug("Not Saving database")
    else:
        songLibrary.save()

    logTextLine("")
    elapsedTimeSecs  = time.time()  - startTime
    logTextLine(f"Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)}")
    logTextLine("")

    log.info(f"End of {myNAME} V{myVERSION}")

    exit(0)