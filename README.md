# Instructions for Usage #
1. Download and install Python 3: https://www.python.org/downloads/
2. Put getngrams.py and your .txt/.csv file in the same directory
 a. Your .txt/.csv file should contain words which are all separated by either a comma or a new line. It doesn’t matter how many words are on a line.
3. Open your command line terminal of choice
    * Windows: I have Windows and like the Ubuntu Windows Subsystem for Linux (WSL), which you can download for free as an app from the Microsoft Store. Other options are Command Prompt or Windows PowerShell, which come pre-installed on all Windows machines.
    * Mac: Terminal
    * Linux: I think it’s just called the command line, but I could be wrong. If you have a Linux machine you probably already know.

4. From the command line, navigate into the directory containing getngrams.py and your words file using cd.
5. Type your program command in with the options you want, press enter, and give the program a minute to run.
    * EXAMPLE instance of running the getngrams.py program:
        `python getgrams.py words.txt -startYear=1800 -endYear=2000 -corpus=eng_2012 -smoothing=0 -caseInsensitive`
    * Your words file can be named anything, not just words.txt, as long as it has a .txt or .csv (comma separated values) file extension
    * `--startYear=`
        * Should be a whole number, minimum 1800
    * `--endYear=`
        * Should be a whole number, maximum 2000
    * `--corpus=`
        * Can be any of the following: eng_us_2012, eng_us_2009, eng_gb_2012, eng_gb_2009, chi_sim_2012, chi_sim_2009, eng_2012, eng_2009, eng_fiction_2012, eng_fiction_2009, eng_1m_2009, fre_2012, fre_2009, ger_2012, ger_2009, heb_2012, heb_2009, spa_2012, spa_2009, rus_2012, rus_2009, ita_2012 (visit        https://books.google.com/ngrams for non-abbreviated list of corpora)
    * `--smoothing=`
        * Should be a whole number, minimum 0. Use 0 for fine-grained data; only use a higher number if you are planning on making a graph of the data and want very smooth lines
    * `--caseInsensitive`
        * Optional. Include in your command to disregard case (that is, consider upper-case and lower-case version of the words to be the same)
  
6. The output file (called frequencies.csv) will appear in the same directory as getngrams.py. You can rename the file to something more specific if you like.
