# createIndex.py
# file 1 for project
import sys
from math import sqrt # for calculating norm of document vector
from porter_martin import PorterStemmer # instantiate stemmer to pass into tokenize

from XMLparser import parse, tokenize, create_stopwords_set

import searchio  # import our own optimized I/O module

# deals with appending to the titleIndex
# store the pageID and title as they appear -- but we don't really need to store them in a datastructure since we're not doing anything special with them
# -- just print them out
#
# input: open file to write to, pageID, title as output from parsing the xml file
def titleIndex_append(f, pageID, titleString):
	f.write(str(pageID)+' '+titleString+'\n')

# handles calculating euclidean norm of document vector -- helper method for calculating wf_t,d
# 		--->>> ||v|| = sqrt(SUM(tf**2 for tf in page_index))
# input: page_index
# output: norm in R of document vector
def docVecNorm(page_index):
	norm = 0
	for term in page_index:
		tf = page_index[term][0]
		norm += tf*tf
	return sqrt(norm)
			
# helper function to createIndex -- forms new post for postings list of index
# input: page_post [tf, [positions]]
# output: new_post [pageID, wf, [positions]]
def formPost(pageID, page_post, page_norm):
	positions = page_post[1]
	tf = page_post[0]
	wf = tf/page_norm
	new_post = [pageID, wf, positions]
	return new_post

# helper to createIndex: after the index is created, must print it to the ii_filename file
# input: filename of index (ii_filename)
#		 total number of docs (N)
#		 index to represent on disk (index)
# index is built in form {'term': [df, [[pageID, wf, [position for position in page]] for each pageID]]}
# write out index in format:  term*df&pageID_0%wf% pos_0 pos_1&pageID_1%wf% pos_0 pos_1 pos2&pageID_2%wf% pos_0
# 		--> print one line for each word in index
def printIndex(ii_filename, N, index):
	# open file to write to
	invertedIndex_file = open(ii_filename, 'w')
	# at top of invertedIndex file, write out total number of documents
	invertedIndex_file.write(str(N)+'\n')
	
	for term in index:
		df = index[term][0]
		term_postings = index[term][1]
		invertedIndex_file.write(term+"*"+str(df)) # so far wrote: word*df

		for i in range(len(term_postings)):
			post = term_postings[i]
			pageID = post[0]
			wf = post[1]
			positions = post[2]

			invertedIndex_file.write("&"+str(pageID)+"%"+str(wf)+"%")
			for pos in positions:
				invertedIndex_file.write(" "+str(pos))
		invertedIndex_file.write("\n")
	
	invertedIndex_file.close()


# input: <stopWords file>, <pagesCollection file>, <invertedIndex to be built>, <titleIndex to be built>
# output: write to the files
def createIndex(stopwords_filename, pagesCollection_filename, ii_filename, ti_filename):
	# open up the files for writing
	titleIndex_file = open(ti_filename, 'w')

	# obtain the stopwords in a set for quick checking
	stopWords_set = create_stopwords_set(stopwords_filename)
	# initialize empty index with structure {'token': [df, [[pageID, wf, [position for position in page]] for each pageID]]}
	index = {}
	# need to keep count of total documents (N) for sake of calculating idf
	N = 0

	# obtain heap mapping pageID's to tuple (list of title words, list of title and text words)
	(collection, maxID) = parse(pagesCollection_filename)
	
	# iterate over keys (pageID's) to fill the index
	for i in range(maxID+1):
		if not i in collection:
			continue
		# otherwise increment total number of documents and process page
		N += 1 # increment total documents

		curr_page_index = {}  # build up temporary dictionary mapping {"term_t": [tf_t, [position for position in page]] for term_t in page}

		item = collection[i]
		pageID = i
		titleString = item[0]
		textString = item[1]
		
		# add to titleIndex:
		titleIndex_append(titleIndex_file, pageID, titleString)

		# tokenize titleString
		# token_list = tokenize(stopWords_set, stemmer, textString)
        token_list = searchio.tokenize(stopWords_set, textString)
		
		# add to index:
		position = 0
		for token in token_list:
			# now put token in curr_page_index dict which has structure {"term_t": [tf_t, [position for position in page]] for term_t in page}
			if not token in curr_page_index:
				# create new temp_postings entry
				curr_page_index[token] = [0,[]] # page_postings entry initialized to [tf=0, positions=[]]

			page_postings = curr_page_index[token]
			page_postings[0] += 1 # increment tf
			page_postings[1].append(position) #append position to postings list
			# now just adjust position
			position += 1
		
		# now curr_page_index built --> need to calculate wf and insert [pageID, wf, [positions]] into index
		# first calculate length of document vector:
		curr_norm = docVecNorm(curr_page_index)
		# now calculate wf for each term in document and insert [pageID, wf, [positions]] into index
		for term in curr_page_index:
			# create new post to insert into index
			new_post = formPost(pageID, curr_page_index[term], curr_norm)
			# insert new post into index
			if not term in index:
				# create new postings entry
				index[term] = [0, []] # postings initialized to [df=0, postings=[]]
			# append post to postings
			postings = index[term]
			postings[0] += 1 # increment df
			postings[1].append(new_post) # append post to postings list

	# now the index is built in form {'term': [df, [[pageID, wf, [position for position in page]] for each pageID]]}
	titleIndex_file.close() # done writing to titleIndex
	# write out index in format:  term*df&pageID_0%wf% pos_0 pos_1&pageID_1%wf% pos_0 pos_1 pos2&pageID_2%wf% pos_0
	#print one line for each word in index 
	printIndex(ii_filename, N, index)
	return index
				
createIndex(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])	
		










