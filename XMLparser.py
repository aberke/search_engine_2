# XML parser used in createIndex

import heapq # using heap to push docIDs as find them in parse

import re

# input: filename (fname) of the stopWords file
# output: set of stopwords
def create_stopwords_set(fname):
    f = open(fname, 'r')
    stopWords_set = set()

    w = f.readline()
    while w != '': # read to EOF
        if w[len(w)-1] == '\n':
            w = w[:len(w)-1] # strip off '\n'
        # add word to set of stopWords
        stopWords_set.add(w)        

        w = f.readline()
    f.close()
    return stopWords_set 

def replace(textString, keepStar):
    t = ''
    for ch in textString:
        if ch.isalnum() or ((ch=='*') and keepStar):
            t += ch
        else:
            t += ' '
    return t

# input: set of stopwords to weed out (stopWords_set)
#        porter stemmer to handle stemming (stemmer)
#        text string to turn into list of tokens (textString)
#        boolean (keepStar) if true: keep '*' in token, else: don't keep '*'
# output: list of tokens
def tokenize(stopWords_set, stemmer, textString, keepStar):
    token_list = []
   
    # 1) lowercase all the words in the stream, 
    textString = textString.lower()
    # 2) obtain the tokens (strings of alphanumeric characters [a-z0-9], terminated by a non alphanumeric character) 
    textString = replace(textString, keepStar)
    # split textString into list of words   
    text_list = textString.split()
    # 3) filter out all the tokens matching element of stopwords list
    token_list = [stemmer.stem(word, 0, len(word) - 1) for word in text_list if not word in stopWords_set]
    
    return token_list


#input: filename (fname) of the file collection
#output: tuple: (dictionary, int):
#        dictionary with key: pageID, value: tuple (titleString, textString)
#        maximum pageID found

def parse(fname):
    f = open(fname)
    pageID = ""
    dictionary = {} # heap initially empty
    maxID = 0

    # loop through entire document by line
    currLine = f.readline()
    while currLine:

        while (not "<id>" in currLine and currLine): currLine = f.readline()
        # currLine now contains the pageID, so parse that as needed
        currLine = currLine.replace("<id>", "")
        currLine = currLine.replace("</id>\n", "")
        if not currLine:
            break
        pageID = int(currLine)

        while (not "<title>" in currLine and currLine): currLine = f.readline()
        # currLine now contains the title, so parse that as needed

        titleString = currLine[7:len(currLine)-9]+'\n'

        #Do we need to remove the \n we added to the titleString??
        textString = titleString 

        while (not "<text>" in currLine and currLine): currLine = f.readline()
        # now we've reached the <text> section, so iterate through lines until reaching the end at </text>
        currLine = currLine.replace("<text>", "")
        while (not "</text>" in currLine and currLine):
            textString = textString + currLine
            currLine = f.readline()

        #now we know we've reached the last line of </text>
        currLine = currLine.replace("</text>", "")
        textString = textString + currLine

        titleTextTuple = titleString, textString
        dictionary[pageID] = (titleString, textString)
        if pageID > maxID:
            maxID = pageID
        currLine = f.readline()

    return (dictionary, maxID)