###############################################################################################################
#  pyMP3duplicate                                                                                             #
#                                                                                                             #
#  The program will scan a given directory and report duplicate MP3 files.                                    #
#                                                                                                             #
#        usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-l] [-v]                                               #
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
import shutil
import pathlib
import textwrap
import datetime
import argparse
import colorama
import myLogger
from tinytag import TinyTag
from _version import myVERSION, myNAME

DIFF = 0.5        # difference in seconds used to determine duplicates.

class Library():
    """  A simple class that wraps the library dictionary.
    """

    def __init__(self):
        self.library = {}

    def hasKey(self, key):
        """  Returns true if the key exist in the library.
        """
        return key in self.library

    def addKey(self, key, item1, item2):
        """  Adds to the library at point key, added is a list of items.
             item1 is song duration.
             item2 is song path.
        """
        l = [item1, item2]
        self.library[key] = l

    def getItem(self, key):
        """  Returns items at position key from the library.
        """
        return self.library[key][0], self.library[key][1]

####################################################################################### checkDuplicate ########
def checkDuplicate(musicFile, tag, key):
    """  A duplicate song has been located that is already in the library.
         The new song already matches the song title and artist, the song
         duration of the two songs are then compared.  If the difference is between
         DIFf seconds then they could be the same.

         DIFF - a named constant.
    """

    songFile, songDuration = songLibrary.getItem(key)

    if abs(tag.duration - songDuration) < DIFF:
        print("-"*80 + "Duplicate Found" + "-"*20)
        print(f"{musicFile} {tag.duration:.2f}")
        print(f"{songFile}  {songDuration:.2f}")
        return True
    else:
        return False


####################################################################################### scanMusic #############
def scanMusic(sourceDir):
    """  Scan the sourceDir, which should contain mp3 files.
         The songs are added to the library using the song artist and title as key.
         If the song already exists in the library, then to two are checked.
    """

    startTime  = time.time()
    count      = 0
    duplicates = 0
    for musicFile in sourceDir.glob("**/*.mp3"):
        try:
            count += 1
            tag = TinyTag.get(musicFile)

            key = f"{tag.artist}:{tag.title}"

            if songLibrary.hasKey(key):
                if checkDuplicate(musicFile, tag, key):
                    duplicates += 1
            else:
                songLibrary.addKey(key, musicFile, tag.duration)

        except (Exception) as error:
            log.error(f"ERROR : {musicFile} :: {error}", exc_info=True)
            print(f"ERROR : {musicFile} :: {error}")

        if (count % 10000) == 0:
            elapsedTimeSecs  = time.time()  - startTime
            print(f"{count}, duplicates {duplicates}: {datetime.timedelta(seconds = elapsedTimeSecs)}")

    print()
    print(f"{colorama.Fore.CYAN} {count} music files found with duplicates {duplicates}. {colorama.Fore.RESET}")

########################################################################################### printSortLicense ######
def printShortLicense():
    print(f"""
{myNAME} V{myVERSION}   Copyright (C) 2020  Kevin Scott
This program comes with ABSOLUTELY NO WARRANTY; for details type `pyBackup -l'.
This is free software, and you are welcome to redistribute it under certain conditions.
    """, flush=True)

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

    #  Add a Positional Argument.
    #  a optional argument would be --source or -s

    parser.add_argument("-s", "--sourceDir", type=pathlib.Path, action="store", default=False, help="directory of the music files [mp3].")
    parser.add_argument("-l", "--license",   action="store_true" , help="Print the Software License.")
    parser.add_argument("-v", "--version",   action="version"    , version=f"{myNAME} V{myVERSION}")

    args = parser.parse_args()

    if args.license:
        printLongLicense()
        exit(0)

    printShortLicense()

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

    return (args.sourceDir)

############################################################################################### __main__ ######

if __name__ == "__main__":

    startTime = time.time()

    songLibrary = Library()             # Create the song library

    log = myLogger.get_logger(myNAME)   # Create the logger.
    log.info("-------------------------------------------------------------")
    log.info(f"Start of {myNAME} V{myVERSION}")

    sourceDir = parseArgs()

    scanMusic(sourceDir)

    print()
    elapsedTimeSecs  = time.time()  - startTime
    print(f"{colorama.Fore.CYAN}Completed  :: {datetime.timedelta(seconds = elapsedTimeSecs)}   {colorama.Fore.RESET}")
    print()

    log.info(f"End of {myNAME} V{myVERSION}")

    exit(0)