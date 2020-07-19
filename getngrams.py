#!/usr/bin/python3
# -*- coding: utf-8 -*

from ast import literal_eval
import pandas as pd
import re
import html.parser
import functools
import requests              
import subprocess
import sys
import os
import argparse


def get_args():
    """
    This function uses the argparse library to parse command line arguments.

    Returns:
        args (argparse.Namespace): An argparse object. Elements of the object 
        can be accessed by their option name as attributes.
    """
    parser = argparse.ArgumentParser(description=
    "This program takes a list of words, or a file containing a list of words,\
 and queries the Google NGram API for the usage frequency of these words, by\
 year, within a desginated time-frame. Unless '--noSave' is indicated, data is\
 saved to a file called 'google_Ngram_output.csv'. A more detailed description\
 of various arguments can be found at https://books.google.com/ngrams/info")

    parser.add_argument("Query", type = str, nargs="+", help="List of words,\
 or CSV or TXT file of words to be queried")

    parser.add_argument("-c", "--corpus", default="eng_2019", type = str, 
        help ="Shorthand name for corpus of words to be queried. Available\
 corpora can be read about at https://books.google.com/ngrams/info. Default is\
 English corpus, 2019 update")

    parser.add_argument("-s", "--startYear", default=1800, type=int,
        help = "A year: beginning of time range to be queried. Default is 1800")

    parser.add_argument("-e", "--endYear", default = 2000, type = int,
        help = "A year: last year of time range to be included in query.\
 Default is 2000")

    parser.add_argument("-sm", "--smoothing", default = 0, type = int,
        help = "The degree to which data points are averaged between years. A\
 smoothing of 0 indicates completely raw data. Default is 0.")

    parser.add_argument("-ci", "--caseInsensitive", action="store_true", 
        help = "Consider upper- and lower-case versions of the words")

    parser.add_argument("-a", "--allData", action="store_true")

    parser.add_argument("-n", "--noSave", action="store_true", 
        help = "Use to prevent data from being saved to external file")

    parser.add_argument("-q", "--quiet", action="store_true",
        help="Use to prevent program from printing to STD OUT")

    parser.add_argument("-o", "--outputDir", default = "./", type = str,
        help = "Directory to save output file to")

    parser.add_argument("-p", "--plot", action="store_true", 
        help = "Create plot of data")

    args = parser.parse_args()
    args.Query = "".join(args.Query).split(",")

    return args


def get_words(args):
    """
    This function takes in a filename of words seperated by either commas,
    newlines, or both, and returns these words in a set.

    Args:
        args (argparse.Namespace): An argparse object. Elements of the object 
        can be accessed by their option name as attributes.

    Returns:
        list of strings : A list of unique words.
    """
    words_list = []
    filename = ""
    # Access words input through commandline, or save name of file given in 
    # command line
    for element in args.Query:
        if element.endswith(".txt") or element.endswith(".csv"):
            filename = element
        else:
            words_list.append(element)

    # collect words from file input from command line
    if len(filename) != 0:
        with open(filename) as in_file:
            for line in in_file:
                line = line.strip()
                words = line.split(",")
                for word in words:
                    words_list.append(word)

    # clean data
    for i in range(len(words_list)):
        word = words_list[i]
        word = word.strip()
        if '?' in word:
            word = word.replace('?', '*')
        if '@' in word:
            word = word.replace('@', '=>')
        words_list[i] = word
    
    return list(set(words_list))


def collect_data(args, words_list):
    """This function runs queries to Google NGram, 9 words at a time. This 
    grouping step is necessary because of restrictions set by the Google NGram 
    viewer itself.

    Args:
        args (argparse.Namespace): An argparse object. Elements of the object 
        can be accessed by their option name as attributes.
        words_list (list of strings): A list of unique words.

    Returns:
        dfs (list of DataFrames): A list of pandas DataFrame objects
    """
    dfs = []
    for i in range(0, len(words_list) - (len(words_list) % 9), 9):
        new_query = ",".join(words_list[i: i + 9]) # create string of 9 or 
                                        # fewer words
        new_df = runQuery(args, new_query)
        dfs.append(new_df)

    # sentinel run
    last_df = runQuery(args, ",".join(words_list[len(words_list) 
                                                    - len(words_list) % 9:]))
    dfs.append(last_df)

    return dfs


def runQuery(args, query):
    """This function processes parameters and submits queries to the getNgrams 
    function. Warning messages are printed for conflicting parameters. Results 
    are printed to standard output. Columns in the dataframe are cleaned, and 
    the dataframe is returned.

    Args:
        args (argparse.Namespace): An argparse object. Elements of the object 
        can be accessed by their option name as attributes.
        query (string): Contains words to be queried

    Returns:
        df (pandas.core.frame.DataFrame): A pandas DataFrame object containing
        word frequency data.
    """
    html_parser = html.parser.HTMLParser()

    # Error handling
    if "*" in query and args.caseInsensitive:
        args.caseInsensitive = False
        print("*NOTE: Wildcard and case-insensitive searches can't be combined,\
 so the case-insensitive option was ignored.")

    elif "_INF" in query and args.caseInsensitive:
        args.caseInsensitive = False
        print("*NOTE: Inflected form and case-insensitive searches can't be\
 combined, so the case-insensitive option was ignored.")

    # get data
    url, urlquery, df = getNgrams(query, args.corpus, args.startYear,
        args.endYear, args.smoothing, args.caseInsensitive)
    url = html_parser.unescape(url).strip()
    urlquery = html_parser.unescape(urlquery).strip()
    list_urlquery = urlquery.split(',')

    # process data
    for i in range(len(list_urlquery)):
        list_urlquery[i] = list_urlquery[i].strip()
        list_urlquery[i] = "".join(list_urlquery[i].split())

    if not args.allData:
        if args.caseInsensitive:
            for col in df.columns:
                col_un = str(html_parser.unescape(col).strip())
                if col.count('(All)') == 1:
                    df[col.replace(' (All)', '')] = df.pop(col)
                elif col.count('(All)') == 0 and col != 'year':
                    if "".join(col_un.split()) not in list_urlquery:
                        df.pop(col)
        
        if '_INF' in query:
            for col in df.columns:
                if '_INF' in col:
                    df.pop(col)
        if '*' in query:
            for col in df.columns:
                if '*' in col:
                    df.pop(col)

        # print output
        if not args.quiet:
            print((','.join(df.columns.tolist())))
            for row in df.iterrows():
                try:
                    print(('%d,' % int(row[1].values[0]) +
                           ','.join(['%.12f' % s for s in row[1].values[1:]])))
                except:
                    print((','.join([str(s) for s in row[1].values])))

        if not args.noSave:
            for col in df.columns:
                if '&gt;' in col:
                    df[col.replace('&gt;', '>')] = df.pop(col)

    return df


def getNgrams(query, corpus_name, startYear, endYear, smoothing, caseInsensitive):
    """
    This function queries data from the Google Ngram database, using 
    user-defined parameters. The results of this query are returned as a 
    pandas DataFrame.

    Args:
        query (string): Contains words to be queried
        corpus_name (string): Shorthand name for corpus of words to be queried
        startYear (int): A year: beginning of time range to be queried
        endYear (int): A year: last year of time range to be included in query
        smoothing (int): The degree to which data points are averaged between 
                            years
        caseInsensitive (bool): Whether or not to consider upper- and 
                                    lower-case versions of the words

    Returns:
        req.url (string): The url representing the query to Google Ngram
        params['content'] (string) : A list of the words being queried
        df (pandas.core.frame.DataFrame): A pandas DataFrame object containing
        word frequency data. 
    """

    # Define parameters
    params = dict(content=query, year_start=startYear, year_end=endYear,
    corpus=corpus_name, smoothing=smoothing,
    case_insensitive=caseInsensitive)

    if params['case_insensitive'] is False:
        params.pop('case_insensitive')
    if '?' in params['content']:
        params['content'] = params['content'].replace('?', '*')
    if '@' in params['content']:
        params['content'] = params['content'].replace('@', '=>')

    req = requests.get('http://books.google.com/ngrams/graph', params=params)
    res = re.findall('ngrams.data = (.*?);\\n', req.text)
    
    if res:
        data = {qry['ngram']: qry['timeseries']
                for qry in literal_eval(res[0])}
        df = pd.DataFrame(data)
        df.insert(0, 'year', list(range(startYear, endYear + 1)))
    else:
        df = pd.DataFrame()

    return req.url, params['content'], df


def output_df(dfs, args):
    """
    This function combines all of the created DataFrame objects into a single 
    DataFrame. The DataFrame is output to 'google_Ngram_output.csv'. A plot 
    is drawn if the user has included the '--plot' flag. 

    Args:
        dfs (list of DataFrames): A list of pandas DataFrame objects to be 
        combined.
        args (argparse.Namespace): An argparse object. Elements of the object 
        can be accessed by their option name as attributes.
    """
    html_parser = html.parser.HTMLParser()
    filename = args.outputDir + "google_Ngram_output.csv"
    bigdf = functools.reduce(lambda x, y: pd.merge(x, y, on = "year",
                                                            how="left"), dfs)
    new_columns = []
    for col in bigdf.columns:
        new_columns.append(html_parser.unescape(col))
    for i in range(len(new_columns)):
        new_columns[i] = new_columns[i].replace("_x", "")
        new_columns[i] = new_columns[i].replace("_y", "")
    bigdf.columns = new_columns
    bigdf.to_csv(filename, index=False, header=True, encoding='utf-8-sig')

    if args.plot:
        try:
            subprocess.call(['python', 'xkcd.py', filename])
        except:
            if args.noSave:
                print(('Currently, if you want to create a plot you ' +
                        'must also save the data. Rerun your query, ' +
                        'removing the -nosave option.'))
            else:
                print(("Plotting Failed: " + filename))


if __name__ == "__main__":
    args = get_args()
    words_list = get_words(args)
    dfs = collect_data(args, words_list)
    output_df(dfs, args)
