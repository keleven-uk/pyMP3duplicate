 PyMP3duplicate.

    The program will scan a given directory and report duplicate MP3 files.

    The main mp3 directory should be scanned first, this will give a list of duplicates in that directory.
    A database is then created of these files keyed on artist, title and duration.
    If any new mp3's need to be added to the main directory, they should be scanned first, this will then
    be compared to the database and any duplicates will be flagged and can be deleted [maybe with the -xS flag].
    The remaining mp3 files can be safely added to the main directory, the database will need to be rebuilt.

    NB : The tags in the new MP3's should be in the same format has the tags in the main directory.
         i.e spaces trimmed and in title case - my preference.
         Also, both mp3's should have valid time or lengths.  Correct with mp3val.

    The database is stored in a simple directory and stored via pickling.  The pickled database is
    stored in the same directory as the main script.

    If a new database needs to be created, then either delete the pickle file or run with the -x flag.

    If the -f flag is used, the duplicates are saved in a file supplied.

    The -d flag sets the time duration, in seconds, of the max difference between two songs.
    If -d flag is not supplied, the default 0.5s will be used.

    The -xS & -xL can be useful for a test run, so the database is left UN-touched.

    Added tqdm - a very cool progress bar for console windows.

    Added the ability to use different modules to read the mp3 tags.
        Currently tinytag, eyed3 & mutagen are supported.

        Tinytag is the fastest, but read only.
        Eyed3 is the next fastest - looks about 3 times slower then Tinytag.
        Mutagen is the slowest, needs to read the song twice - about five time slower then mutagen.

    Added the ability to ignore certain duplicates files, these may be files with the same
      artist, title and duration [or close] but are in fact not the same track.


usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-d DIFFERANCE] [-xL] [-xS] [-b] [-n] [-l] [-v]

A Python MP3 Duplicate finder.
-----------------------
The program will scan a given directory and report duplicate MP3 files.

optional arguments:
  -h, --help            show this help message and exit

  -s SOURCEDIR, --sourceDir SOURCEDIR
                        directory of the music files [mp3].

  -f DUPFILE, --dupFile DUPFILE
                        [Optional] list duplicates to file.

  -d DIFFERENCE, --difference DIFFERENCE
                        Time difference between songs, default = 0.5s.

  -xL, --noLoad         Do not load database.

  -xS, --noSave         Do not save database.

  -b, --build           Build the database only.

  -n, --number          print the Number of Songs in the database.

  -l, --license         Print the Software License.

  -v, --version         show program's version number and exit


 Kevin Scott (C) 2020 :: pyMP3duplicate V1.1.1




For changes see history.txt
