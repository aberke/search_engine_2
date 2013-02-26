# createIndex.py
# file 1 for project
import sys
import heapq # using heap to push docIDs as find them in parse
from porter_martin import PorterStemmer # instantiate stemmer to pass into tokenize

from XMLparser import parse, tokenize, create_stopwords_set

# deals with appending to the titleIndex
# store the pageID and title as they appear -- but we don't really need to store them in a datastructure since we're not doing anything special with them
# -- just print them out
#
# input: open file to write to, pageID, title as output from parsing the xml file
def titleIndex_append(f, pageID, titleString):
	f.write(str(pageID)+' '+titleString+'\n')


# input: <stopWords file>, <pagesCollection file>, <invertedIndex to be built>, <titleIndex to be built>
# output: write to the files
def createIndex(stopwords_filename, pagesCollection_filename, ii_filename, ti_filename):
	# open up the files for writing
	invertedIndex_file = open(ii_filename, 'w')
	titleIndex_file = open(ti_filename, 'w')
	# instantiate stemmer to pass into tokenize
	stemmer = PorterStemmer()

	# obtain the stopwords in a set for quick checking
	stopWords_set = create_stopwords_set(stopwords_filename)
	# initialize empty index
	index = {}

	# obtain heap mapping pageID's to tuple (list of title words, list of title and text words)
	(collection, N) = parse(pagesCollection_filename)
	
	# iterate over keys (pageID's) to fill the index
	for i in range(N+1):

		if not i in collection:
			continue
		item = collection[i]
		#pageID = item[0]
		pageID = i
		titleString = item[0]
		textString = item[1]
		
		# add to titleIndex:
		titleIndex_append(titleIndex_file, pageID, titleString)

		# tokenize titleString
		token_list = tokenize(stopWords_set, stemmer, textString)
		
		# add to index:
		position = 0
		for token in token_list:
			# now put word/token in index which has structure: 
				#{'token': [[pageID, [position for position in page] for each pageID]}
			if not token in index:
				# create new entry in index:  
				index[token] = [] # postings list initialized to empty list
			

			postings = index[token]
			# check if we need to add position to already posted document
			if (len(postings) > 0) and (pageID == postings[len(postings)-1][0]):
				# append position
				positions = postings[len(postings)-1][1]
				positions.append(position)
			else:
				# append document
				postings.append([pageID, [position]])

			# now just adjust position
			position += 1
	# now the index is built
	titleIndex_file.close() # done writing to titleIndex
	
	# write out index in format:  word&pageID_0%pos_0 pos_1&pageID_1%pos_0 pos_1 pos2&pageID_2 pos_0
	#print one line for each word in index 
	for word in index:
		w_postings = index[word]
		invertedIndex_file.write(word)
		invertedIndex_file.write("".join(["&%s%%%s" % (str(w_postings[i][0]), " ".join([str(x) for x in w_postings[i][1]])) for i in range(len(w_postings))]))
		invertedIndex_file.write("\n")
	
	invertedIndex_file.close()
	return index
				
createIndex(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])	
		










