###############################################################################################################
#    args   Copyright (C) <2023>  <Kevin Scott>                                                               #
#                                                                                                             #
#    Parse the command line arguments.                                     .                                  #
#                                                                                                             #
#   options:                                                                                                  #
#     -h, --help            show this help message and exit                                                   #
#     -s SOURCEDIR, --sourceDir SOURCEDIR                                                                     #
#                           directory of the music files [mp3].                                               #
#     -f DUPFILE, --dupFile DUPFILE                                                                           #
#                           [Optional] list duplicates to file, start afresh.                                 #
#     -fA DUPFILEAMEND, --dupFileAmend DUPFILEAMEND                                                           #
#                           [Optional] list duplicates to file, Amend to previous.                            #
#     -d DIFFERENCE, --difference DIFFERENCE                                                                  #
#                           Time difference between songs, default = 0.5s.                                    #
#     -b, --build           Build the database only.                                                          #
#     -n, --number          Print the Number of Songs in the database.                                        #
#     -l, --license         Print the Software License.                                                       #
#     -v, --version         Print the version of the application.                                             #
#     -e, --explorer        Load program working directory into file explorer.                                #
#     -t, --checkThe        Check for a artist for trailing ',the'.                                           #
#     -c, --check           Check database integrity.                                                         #
#     -cD, --checkDelete    Check database integrity and delete unwanted.                                     #
#     -xL, --noLoad         Do not load database.                                                             #
#     -xS, --noSave         Do not save database.                                                             #
#     -np, --noPrint        Do Not Print Possible False Positives.                                            #
#     -zD, --zapNoneMusic   Zap [DELETE] none music files.                                                    #
#                                                                                                             #
#                                                                                                             #
#     For changes see history.txt                                                                             #
#                                                                                                             #
###############################################################################################################
#    Copyright (C) <2022>  <Kevin Scott>                                                                      #
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
import textwrap
import argparse
import colorama

from pathlib import Path

import src.License as License
import src.utils.duplicateUtils as duplicateUtils

############################################################################################## parseArgs ######
def parseArgs(appName, appVersion, logger):
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
        epilog=f" Kevin Scott (C) 2020-2023 :: {appName} {appVersion}")

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
        License.printShortLicense(appName, appVersion, "", False)
        print(f"Running on {sys.version} Python")
        logger.info(f"Running on {sys.version} Python")
        logger.info(f"End of {appName} V{appVersion}: version")
        print("Goodbye.")
        sys.exit(0)

    if args.license:
        License.printLongLicense(appName, appVersion)
        logger.info(f"End of {appName} V{appVersion} : Printed Licence")
        print("Goodbye.")
        sys.exit(0)

    if not args.sourceDir and not (args.check or args.checkDelete or args.number or args.explorer):
        logger.error("No Source Directory Supplied.")
        print(f"{colorama.Fore.RED}No Source Directory Supplied. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        sys.exit(1)

    if args.sourceDir and not args.sourceDir.exists():  # Only check source dir exits if one was entered.
        logger.error("Source Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Source Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        sys.exit(2)

    if args.dupFile and not args.dupFile.parent.exists():  # Only check Duplicate File Directory exits if one was entered.
        logger.error("Duplicate File Directory Does Not Exist.")
        print(f"{colorama.Fore.RED}Duplicate File Directory Does Not Exist. {colorama.Fore.RESET}")
        parser.print_help()
        print("Goodbye.")
        sys.exit(3)

    if args.dupFile:  # Delete duplicate file if it exists.
        try:
            dfile = args.dupFile
            os.remove(args.dupFile)
        except (IOError, os.error):
            logger.error("Duplication File Does Not Exist.")  # Log error, but don't really care.
    else:  # Amend to previous duplicate file, if it exists.
        dfile = args.dupFileAmend

    if args.number :
        License.printShortLicense(appName, appVersion, dfile, False)
        l = songLibrary.noOfItems
        print(f"Song Library has {l} songs")                 # Print on number of songs in library.
        print("Goodbye.")
        sys.exit(0)

    if args.explorer:
        duplicateUtils.loadExplorer(logger)             # Load program working directory n file explorer.
        print("Goodbye.")
        sys.exit(0)

    checkDB = 0
    if args.check:
        checkDB = 1                    # Run data integrity check in test mode on library.
    elif args.checkDelete:
        checkDB = 2                    # Run data integrity check in delete mode on library.

    return (args.sourceDir, dfile, args.noLoad, args.noSave, args.build, args.difference, args.noPrint, args.zapNoneMusic, args.checkThe, checkDB)

