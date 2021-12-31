###############################################################################################################
#    zapUtils.py   Copyright (C) <2020-2021>  <Kevin Scott>                                                   #                                                                                                             #                                                                                                             #
#    Will scan a given directory and remove empty dirs and unwanted files.                                    #
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
from send2trash import send2trash

import src.Timer as myTimer
import src.License as myLicense
import src.utils.duplicateUtils as duplicateUtils

timer = myTimer.Timer()

############################################################################################## removeEmptyDir( #######
def removeUnwanted(sourceDir, duplicateFile, emptyDir, zap, recycle, logger):
    """ Scan and delete empty directories and zap Non Music files.
        Will remove empty dirs if emptyDir is true, set in config file.
        Will remove non music files if zap is true, set at command line.
        will use rec bin if recycle is true.

        NB : Cannot use fileList, need to look at dirs and all files not just .mp3 files.
             Therefore need to scan file system again.
    """

    timeDir = myTimer.Timer()
    timeDir.Start

    noOfDirs = 0
    nonMusic = 0
    message  = ""

    print("\nRunning Empty Directory Check and zap Non Music files.\n")
    logger.info("Running Empty Directory Check and zap Non Music files.")

    for musicFile in sourceDir.glob("**/*"):
        if emptyDir and musicFile.is_dir():
            if not len(os.listdir(musicFile)):
                noOfDirs += 1
                duplicateUtils.logTextLine("-" * 70 + "Empty Directory Deleted" + "-" * 40, duplicateFile)
                duplicateUtils.logTextLine(f"{musicFile}", duplicateFile)
                zapEmptyDir(musicFile, recycle)

        if zap and musicFile.is_file():
            if musicFile.suffix != ".mp3":                  # A non music file found.
                if musicFile.suffix == ".pickle": continue  # Ignore database if stored in target directory.
                if musicFile.suffix == ".json"  : continue  # Ignore database if stored in target directory.
                duplicateUtils.logTextLine("-" * 80 + "Non Music File Found" + "-" * 40, duplicateFile)
                duplicateUtils.logTextLine(f"{musicFile} is not a music file and has been deleted.", duplicateFile)
                zapFile(musicFile, recycle)
                nonMusic += 1

    if nonMusic != 0:
        message += f" Removed {nonMusic} non music files."

    if noOfDirs != 0:
        message += f" Removed {noOfDirs} empty directories in {timeDir.Stop}."

    if message != "":
        print(message)
        duplicateUtils.logTextLine("", duplicateFile)
        duplicateUtils.logTextLine(message, duplicateFile)
        logger.info(message)

################################################################################################## zapEmptyDir ######
def zapEmptyDir(musicFile, recycle):
    """ Zap [delete] any empty dir."""

    try:
        if recycle:
            send2trash(str(musicFile))  # Move to recycle bin.
        else:
            shutil.rmtree(musicFile, ignore_errors=True, onerror=None)  # Permanently remove directory
    except OSError:
        logger.error(f"ERROR : Can't delete Directory : {musicFile}")

############################################################################################## zapNoneMusicFile ######
def zapFile(musicFile, recycle):
    """ Zap [delete] any none music file."""

    try:
        if recycle:
            send2trash(str(musicFile))
        else:
            os.remove(musicFile)
    except OSError:
        logger.error(f"ERROR : Can't delete file : {musicFile}")
