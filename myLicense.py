###############################################################################################################
#                                                                                                             #
#  Two procedure to print out License information, one short and one long.                                    #
#  One procedure to either print test to screen or a file.                                                    #
#                                                                                                             #
#       Kevin Scott     2020                                                                                  #
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

########################################################################################### printSortLicense ######
def printShortLicense(Name, Version, textFile):
    logTextLine("", textFile)
    logTextLine(f"{Name} V{Version}   Copyright (C) 2020  Kevin Scott", textFile)
    logTextLine(f"This program comes with ABSOLUTELY NO WARRANTY; for details type `{Name} -l'.", textFile)
    logTextLine("This is free software, and you are welcome to redistribute it under certain conditions.", textFile)

########################################################################################### printLongLicense ######
def printLongLicense(Name, Version):
    print(f"""
    {Name} V{Version}  Copyright (C) 2020  Kevin Scott

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