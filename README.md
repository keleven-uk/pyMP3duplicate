 PyMP3duplicate.

    The program will scan a given directory and report duplicate MP3 files.

    The main mp3 directory should be scanned first, this will give a list of duplicates in that directory.
    A database is then created of these files keyed on artist, title and duration.
    If any new mp3's need to be added to the main directory, they should be scanned first, these will then
    be compared to the database and any duplicates will be flagged and can be deleted.
    The remaining mp3 files can be safely added to the main directory.

    The database is stored in a simple directory and stored via pickling.  The pickled database is
    stored in the same directory ans the man script.

    If a new database needs to be created, then either delete the pickle file or run with the -x flag.

    If the -f flag is used, the duplicates are saved in a file supplied.


usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-xL] [-xS] [-b] [-n] [-l] [-v]

A Python MP3 Duplicate finder.
-----------------------
The program will scan a given directory and report duplicate MP3 files.

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCEDIR, --sourceDir SOURCEDIR
                        directory of the music files [mp3].
  -f DUPFILE, --dupFile DUPFILE
                        [Optional] list duplicates to file.
  -xL, --noLoad         Do not load database.
  -xS, --noSave         Do not save database.
  -b, --build           Build the database only.
  -n, --number          print the Number of Songs in the database.
  -l, --license         Print the Software License.
  -v, --version         show program's version number and exit

 Kevin Scott (C) 2020 :: pyMP3duplicate V1.0.2



For changes see history.txt
