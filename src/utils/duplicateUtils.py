###############################################################################################################
#    duplicateUtils.py   Copyright (C) <2020-2021>  <Kevin Scott>                                             #                                                                                                             #                                                                                                             #
#    A number of helper and utility functions                                                                 #
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
from tqdm import tqdm

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
    exit(0)


####################################################################################### checkToIgnore #########
def checkToIgnore(musicDuplicate, songDuplicate, ignore):
    """  Each song may carry a ignore flag, return True if these are the same.
         Only checked if the tags are read using mutagen.
    """
    return (musicDuplicate == ignore) and (songDuplicate == ignore)


####################################################################################### countSongs ############
def countSongs(sourceDir, fileList, NCOLS):
    """  Count the number of songs [.mp3 files] in the sourceDir.
         The filename are save in a list fileList, this is then passed to scanMusic.
         Takes just over a second at 160000 files approx.
    """
    count = 0

    print("Counting Songs")
    for musicFile in tqdm(sourceDir.glob("**/*.mp3"), unit="songs", ncols=NCOLS, position=1):
        fileList.append(musicFile)

    print(f"... with a song count of {len(fileList)}")
    return len(fileList)


####################################################################################### printDuplicate ########
def logTextLine(textLine, textFile):
    """  if the textFile is set, then write the line of text to that file, else print to screen.

         textLine needs to be a string, for f.write - NOT a path.
    """
    if textFile:
        with open(textFile, encoding='utf-8', mode="a") as f:     # Open in amend mode, important.
            f.write(textLine + "\n")
    else:
        print(textLine)
