# query index
import sys
# need sqrt and floor so that skips can occur every floor(sqrt(L)) pageID's where L = #pageID's
from math import sqrt# used for calculating skip pointers
import heapq # using heap to sort postings lists by length so we can begin ANDing with smallest list
from porter_martin import PorterStemmer # instantiate stemmer to pass into tokenize
from bool_parser import bool_expr_ast as bool_parse # provided boolean parser for python2.6

from XMLparser import tokenize, create_stopwords_set

#word&pageID_0%pos_0 pos_1&pageID_1%pos_0 pos_1 pos2&pageID_2%pos_0

# reconstructs the invertedIndex that createIndex made by reading from file
# input: filename of inverted index file
# output: inverted index
def reconstruct_Index(ii_filename):
	# reconstruct invertedIndex from file starting with empty dictionary
	index = {} 
	ii_file = open(ii_filename)

	line = ii_file.readline()
	while line != '': # read to EOF
		# TODO: REPLACE THIS WITH MORE EFFICIENT PARSER
		l = line.split('&') # split along the postings delimeter   [word, [post0],[post1],...]
		
		# extract word 
		word = l[0]

		# build postings list from empty list
		postings = []
		for i in range(1, len(l)):
			p = l[i].split('%')
			positions = [int(pos) for pos in p[1].split()]
			posting = [int(p[0]), positions] # posting = [pageID, positions] 
			postings.append(posting)

		index[word] = postings
		line = ii_file.readline()

	ii_file.close()
	return index

# helper functions to 
# input: two positions lists: positions_1 corresponds to the positions list of the first word, positions_2 corresponds to the positions list of second word
#		 i_difference: (index of token2) - (index of token1) in the query.  Essentially, the positional difference of the two tokens
# output: new (intersection) positions list that contains exactly the entries of positions_1 
#			where there is an entry in positions_2 that is one position after a position in positions_1
# Note of use:
#	This function is meant to be called iteratively, so that if the PQ is "Space Adventure 2001", we take:
#								>>> PQ_AND(PQ_AND(index['Adventure'], index['Space'], -1), index['2001'], 2)
#									  	where len(index['Adventure']) < len(index['Spage']) < len(index['2001'])
def positions_AND(positions_1, positions_2, i_difference):
	intersection = []
	posIndex_1 = 0
	posIndex_2 = 0
	length_1 = len(positions_1)
	length_2 = len(positions_2)

	while (posIndex_1 < length_1) and (posIndex_2 < length_2):
		position_1 = positions_1[posIndex_1]
		position_2 = positions_2[posIndex_2]

		if (position_1+i_difference) == position_2:
			# found a match!
			intersection.append(position_2) # we append position 2 so that this can be called iteratively starting with the left-most position
			# increment both indecies
			posIndex_1 += 1
			posIndex_2 += 1

		elif (position_1+i_difference) < position_2:
			posIndex_1 += 1

		else: # (position_1+i_difference > position_2)
			posIndex_2 += 1

	return intersection

# helper to both handle_BQ and handle_PQ -- handles the AND
# takes two postings lists and 3rd parameter which for the purpose of this function can be interpreted as a boolean stating whether this is for handle_PQ or handle_BQ:
#			False (handle_BQ): is passed as 0 and means this is for the BQ_AND and there should be no further call to positional_AND
#			True (handle_PQ): means any other value, which is passed in as the difference of the indecies of query1 and query2, for the sake of the positional_AND.
#				--> If true, function uses helper procedure positional_AND 
#		if true: returns the intersection over the pageID's
#		if false: returns the intersection over the pageID's and positions (where position_2 directly after position_1)
def postings_AND(postings_1, postings_2, i_difference):
	intersection = []  # Even if just matching PageID's, I want this to still be a full postings list rather than just pageIDs so that we can iterate on this function with ease
	pageIndex_1 = 0
	pageIndex_2 = 0
	length_1 = len(postings_1)
	length_2 = len(postings_2)
	# instead of storing skip pointers, we use skip pointers by just indexing in sqrt(len(list)) ahead to check if we should skip
	skip_1 = int(sqrt(length_1)) # precalculated skip for postings_1
	skip_2 = int(sqrt(length_2)) # precalculated skip for postings_2

	while (pageIndex_1 < length_1) and (pageIndex_2 < length_2):
		post_1 = postings_1[pageIndex_1]
		post_2 = postings_2[pageIndex_2]
		pageID_1 = post_1[0]
		pageID_2 = post_2[0]
		if pageID_1 == pageID_2: # pageID's match!
			if not i_difference: 
				# we're just ANDing over pageIDs so we reached a match
				intersection.append(post_1) # keep that post since it belongs in intersection
			else: 
				# we're also matching positions, so keep checking for match in positions
				positions_1 = post_1[1]
				positions_2 = post_2[1]
				position_intersection = positions_AND(positions_1, positions_2, i_difference) # take intersection of positions lists
				# only append to intersection if positions_intersection is a nonempty list
				if position_intersection:
					intersection.append([pageID_1, position_intersection])
			# increment both page indecies
			pageIndex_1 += 1 
			pageIndex_2 += 1
		elif pageID_1 < pageID_2:
			# we'll either skip ahead in postings_1 or just increase its index by 1
			skip_pointer = pageIndex_1 + skip_1
			# check that skip_pointer doesn't exceed length and if its worth skipping to
			if (skip_pointer < length_1) and (postings_1[skip_pointer][0] <= pageID_2): 
				# skip to skip pointer!
				pageIndex_1 = skip_pointer
			else: # no skip pointer, so just increase by 1
				pageIndex_1 += 1
		else: # pageID_1 > pageID_2
			# we'll either skip ahead in postings_1 or just increase its index by 1
			skip_pointer = pageIndex_2 + skip_2
			if (skip_pointer < length_2) and (postings_2[skip_pointer][0] <= pageID_1):
				# skip to skip pointer!
				pageIndex_2 = skip_pointer
			else:
				pageIndex_2 += 1
	return intersection

# helper to handle_PQ -- handles the AND
# takes two postings lists and returns the intersection over the pageID's and positions 
# takes as 3rd parameter: difference in indecies of words in query that correspond to the postings.  This is for the purpose of the positional ANDing
#	(each entry (pageID, position) in postings_1 that appears in intersection, has a corresponding entry (pageID, position+i_difference) that appears in postings_2)
# uses helper function postings_AND which then also uses positions_AND
def PQ_AND(postings_1, postings_2, i_difference):
	return postings_AND(postings_1, postings_2, i_difference)

# helper to handle_BQ -- handles the AND
# takes two postings lists and returns the intersection over the pageID's
# uses helper function postings_AND
def BQ_AND(postings_1, postings_2):
	return postings_AND(postings_1, postings_2, 0)


def postings_OR(postings_1, postings_2):
	# if one of the postings is empty, trivially return other postings list
	if not postings_1:
		return postings_2
	if not postings_2:
		return postings_1

	union = [] # I want this to still be a full postings list rather than just pageIDs so that we can continue to utilize skip-pointers in further iterations
	i_1 = 0
	i_2 = 0
	while 1:
		# check if we're at the end of one of the postings lists
		if i_1 == len(postings_1):
			# tack on the rest of the postings_2 to union and we're done
			while i_2 < len(postings_2):
				if postings_1[i_1-1][0] != postings_2[i_2][0]:
					union.append(postings_2[i_2])
				i_2 += 1
			break

		if i_2 == len(postings_2):
			# tack on the rest of the postings_1 to union and we're done
			while i_1 < len(postings_1):
				if postings_2[i_2-1][0] != postings_1[i_1][0]:
					union.append(postings_1[i_1])
				i_1 += 1
			break
		# verified we're not at the end of one of the postings lists
		post_1 = postings_1[i_1]
		post_2 = postings_2[i_2]
		pageID_1 = post_1[0]
		pageID_2 = post_2[0]
		
		if pageID_1 == pageID_2:
			union.append(post_1)
			i_1 += 1
			i_2 += 1
		elif pageID_1 < pageID_2:
			union.append(post_1)
			i_1 += 1
		else: #pageID_1 > pageID_2
			union.append(post_2)
			i_2 += 1

	return union

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 boolean expression (expr) -- that this function is called recursively on
# output: postings-list that satisfies boolean expression (expr)
def handle_BQ_expr(stopwords_set, index, stemmer, expr):
	# base case
	if type(expr) == str:
		token = tokenize(stopwords_set, stemmer, expr)[0]
		if token in index:
			return index[token]
		else:
			return []
	else:
		operator = expr[0] # AND or OR
		arguments = expr[1] # list of boolean expressions (base case is that they're just words)
		base_postings = []

		if operator == 'OR':
			for arg in arguments:
				base_postings = postings_OR(base_postings, handle_BQ_expr(stopwords_set, index, stemmer, arg))
			return base_postings
		else: # operator == 'AND'
			heap = [] # want to first sort arguments postings by length so we can being ANDing with smallest list
			for arg in arguments:
				postings = handle_BQ_expr(stopwords_set, index, stemmer, arg)
				heapq.heappush(heap, (len(postings), postings))

			base_postings = heapq.heappop(heap)[1]
			heap_len = len(heap)
			for j in range(len(heap)):
				postings = heapq.heappop(heap)[1]
				base_postings = BQ_AND(base_postings, postings)
			return base_postings
			 
# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
def handle_BQ(stopwords_set, index, stemmer, query):
	# ('OR', ['Her', ('OR', ['This', 'That']), ('OR', ['This', 'That'])])

	# for now we assume we get well formed Boolean queries with no stopwords
	bool_expr = bool_parse(query)
	postings = handle_BQ_expr(stopwords_set, index, stemmer, bool_expr)
	docs = ''
	for k in range(len(postings)):
		if k > 0:
			docs += ' '
		docs += str(postings[k][0])
	return docs

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
# output: prints out the matching documents in order of pageID
# 			for PQ matching documents contain subsequence [t1, t2, .., tk] in this order with adjacent terms
def handle_PQ(stopwords_set, index, stemmer, query):
	# obtain stream of terms from query -- also handles removing operators "" and newline '\n'
	stream_list = tokenize(stopwords_set, stemmer, query)
	# initialize variables in greater scope
	intersection = []
	tup = None

	heap = [] # I use a heap to first sort out which postings lists are smallest -- so that my ANDing can be efficient
	for i in range(len(stream_list)):
		word = stream_list[i]
		if not word in index: 
			# word isn't in index, so we can satisfy positional query -- return no documents
			return ''
		else:
			# otherwise, store postings in heap, where heap sorts by length of postings.  Also need to store index of work in query for the positional AND
			postings = index[word]
			tup = (len(postings), (i, postings)) # stores in heap: (len(postings), (indexInQuery, postings))
			heapq.heappush(heap, tup)

	num_tokens = len(heap)
	i_1 = 0
	i_2 = 0
	if not num_tokens:
		return ''
	else:
		tup = heapq.heappop(heap)
		i_1 = tup[1][0]
		intersection = tup[1][1]

	for j in range(1, num_tokens):
		tup = heapq.heappop(heap)
		i_2 = tup[1][0]
		postings = tup[1][1]
		# update intersection by intersecting on current intersection, and newly retrieved postings list.  
		intersection = PQ_AND(intersection, postings, i_2-i_1) # We send in the difference of the indecies of the words in query for the positional AND
		if not intersection:
			# if nothing is left in intersection, can break out of loop now with nothing to return
			return ''
		else:
			i_1 = i_2 # otherwise update our indecies for the purpose of the parameters for positional AND

	docs = ''
	for k in range(len(intersection)):
		if k > 0:
			docs += ' '
		docs += str(intersection[k][0])

	return docs



# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
# output: prints out the matching documents in order of pageID
# 			for FTQ matching documents contain at least one word whose stemmed version is one of the ti's
def handle_FTQ(stopwords_set, index, stemmer, query):
	# turn query into stream of tokens
	stream_list = tokenize(stopwords_set, stemmer, query)
	stream_length = len(stream_list)
	if not stream_length: # make sure we got some tokens out of that query
		return ''
	# initialize union to empty list
	union = []

	for i in range(stream_length):
		word = stream_list[i]
		if word in index:
			union = postings_OR(union, index[word])

	documents = ''
	for j in range(len(union)):
		if j > 0:
			documents += ' '
		pageID = union[j][0]
		documents += str(pageID)	
	return documents

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
# helper routine to queryIndex -- determines type of query and passes off to further handling
def handle_query(stopwords_set, index, stemmer, query):
	# determine query type (OWQ, FTQ, PQ, BQ)
	if ('AND' in query or 'OR' in query or ')' in query or '(' in query):  # note that the boolean parser strips off trailing '\n'
		# handle BQ in its own way
		return handle_BQ(stopwords_set, index, stemmer, query)
	
	if (query[0]=='"' and query[len(query)-2]=='"' and query[len(query)-1]=='\n') or (query[0]=='"' and query[len(query)-1]=='"'): # it's a PQ
		return handle_PQ(stopwords_set, index, stemmer, query)
		
	else: # it's a OWQ or FTQ
		return handle_FTQ(stopwords_set, index, stemmer, query)

# main function
def queryIndex(stopwords_filename, ii_filename, ti_filename):
	index = reconstruct_Index(ii_filename)
	stopwords_set = create_stopwords_set(stopwords_filename)
	# instantiate stemmer to pass into tokenize
	stemmer = PorterStemmer()
	while 1: # read queries from standard input until user enters CTRL+D
		#print(count)
		try:
			query = sys.stdin.readline()
		except KeyboardInterrupt:
			break
		if not query:
			break
		documents = handle_query(stopwords_set, index, stemmer, query)
		print(documents)
	return	

queryIndex(sys.argv[1], sys.argv[2], sys.argv[3])

