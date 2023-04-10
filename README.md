 PyMP3duplicate.

    The program will scan a given directory and report duplicate MP3 files.
    
    The main mp3 directory should be scanned first, this will give a list of duplicates in that directory.
    A database is then created of these files keyed on artist, title and duration.
    If any new mp3's need to be added to the main directory, they should be scanned first, this will then
    be compared to the database and any duplicates will be flagged and can be deleted [maybe with the -xS flag].
    The remaining mp3 files can be safely added to the main directory, the database will need to be rebuilt.
    
    NB : The tags in the new MP3's should be in the same format has the tags in the main directory.
         i.e spaces trimmed and in title case - my preference. [See note about Soundex later on.]
         Also, both mp3's should have valid time or lengths.  Correct with mp3val.
    
    The database is stored in a simple directory and stored via pickling.  The pickled database is
    stored in the same directory as the main script, if location not set in config file..
    
    If a new database needs to be created, then either delete the pickle file or run with the -xL flag.
    
    If the -f flag is used, the duplicates are saved to the file supplied.
    If the -f flag not supplied, the duplicates are listed to the screen [standard output].
    
    The -d flag sets the time duration, in seconds, of the max difference between two songs.
    If the -d flag is not supplied, the default 0.5s will be used.
    
    The -xS & -xL can be useful for a test run, so the database is left UN-touched.
    
    The -zD flag if specified zap [delete] none music files.
        Delete to recycle bin or plainf delete is set via a user option.
        Will find and delete empty directories, selectable by user option.
    
    Added tqdm - a very cool progress bar for console windows.
    
    Added the ability to use different modules to read the mp3 tags.
        Currently tinytag, Eyed3 & Mutagen are supported.
    
        Tinytag is the fastest, but read only.
        Eyed3 is the next fastest - looks about 3 times slower then Tinytag [but gives errors to the screen].
        Mutagen is the slowest, needs to read the song twice - about five time slower then mutagen.
    
    Added the ability to ignore certain duplicates files, these may be files with the same
      artist, title and duration [or close] but are in fact not the same track.
    
    Added the ability to match the song artist / title using the Soundex algorithm, to add a sort of
    fuzzy matching.  Also will ignore any leading 'the'.  Also, the matching is done with lower case strings.
      i.e The Sweet will match Sweet and Led Zeppelin should match Led Zepelin.

To install dependencies pip -r requirements.txt

usage: pyMP3duplicate.py [-h] [-s SOURCEDIR] [-f DUPFILE] [-fA DUPFILEAMEND] [-d DIFFERENCE] [-b] [-n] [-l] [-v] [-e] [-t] [-c] [-cD] [-xL] [-xS] [-np] [-zD]
::
    A Python MP3 Duplicate finder.
    -----------------------
    The program will scan a given directory and report duplicate MP3 files.

    options:
    
    -h, --help            show this help message and exit.
    
    -s SOURCEDIR, --sourceDir SOURCEDIR
                            directory of the music files [mp3].
    
    -f DUPFILE, --dupFile DUPFILE
                            [Optional] list duplicates to file, start afresh.
    
    -fA DUPFILEAMEND, --dupFileAmend DUPFILEAMEND
                            [Optional] list duplicates to file, Amend to previous.
    
    -d DIFFERENCE, --difference DIFFERENCE
    
                            Time difference between songs, default = 0.5s.
    -b, --build           Build the database only.
    
    -n, --number          Print the Number of Songs in the database.
    
    -l, --license         Print the Software License and exit.
    
    -v, --version         Print the version of the application and exit.
    
    -e, --explorer        Load program working directory into file explorer.
    
    -t, --checkThe        Check for a artist for trailing ',the'.
    
    -c, --check           Check database integrity.
    
    -cD, --checkDelete    Check database integrity and delete unwanted.
    
    -xL, --noLoad         Do not load database.
    
    -xS, --noSave         Do not save database.
    
    -np, --noPrint        Do Not Print Possible False Positives.
    
    -zD, --zapNoneMusic   Zap [DELETE] none music files.
    
    
    Kevin Scott (C) 2020-2023 :: pyMP3duplicate 2023.44

For changes see history.txt
