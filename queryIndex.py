# use provided btrees for wildcard queries
from BTrees.OOBTree import OOBTree
# query index
import sys
# need sqrt and floor so that skips can occur every floor(sqrt(L)) pageID's where L = #pageID's
from math import sqrt# used for calculating skip pointers
from math import log # used for calculating inverse document frequency (idf)
import heapq # using heap to sort postings lists by length so we can begin ANDing with smallest list
from porter_martin import PorterStemmer # instantiate stemmer to pass into tokenize
from bool_parser import bool_expr_ast as bool_parse # provided boolean parser for python2.6

from XMLparser import tokenize, create_stopwords_set
from queryIndex_util import updateScores

import searchio  # import our own optimized I/O module

# index form: {'term': [df, [[pageID, wf, [position for position in page]] for each pageID]]}
# SHOULD BE REPLACED WITH:
#		{'term': [df, (function to retrieve postings list from file)]}

# index written to file in format:  term*df&pageID_0%wf% pos_0 pos_1&pageID_1%wf% pos_0 pos_1 pos2&pageID_2%wf% pos_0

# reconstructs the invertedIndex that createIndex made by reading from file
# input: filename of inverted index file
# output: inverted index, N (total number of documents)
def reconstruct_Index(ii_filename):
	return searchio.loadIndex(ii_filename)

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
	# instead of storing skip pointers, we use skip pointers by just indexing in sqrt(len(list)) ahead to check if we should skip
	skip_1 = int(sqrt(length_1)) # precalculated skip for postings_1
	skip_2 = int(sqrt(length_2)) # precalculated skip for postings_2

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
			# we'll either skip ahead in positions_1 or just increase index by 1
			skip_pointer = posIndex_1 + skip_1
			# check that skip_pointer doesn't exceed length and if its worth skipping to
			if (skip_pointer < length_1) and ((positions_1[skip_pointer] + i_difference) <= position_2):
				# skip to the skip pointer
				posIndex_1 = skip_pointer
			else:
				posIndex_1 += 1

		else: # (position_1+i_difference > position_2)
			# we'll either skip ahead in positions_2 or just increase its index by 1
			skip_pointer = posIndex_2 + skip_2
			if (skip_pointer < length_2) and (positions_2[skip_pointer] <= (position_1 + i_difference)):
				posIndex_2 = skip_pointer
			else:
				posIndex_2 += 1

	return intersection

# helper to both handle_BQ and handle_PQ -- handles the AND
# input: postings_1: current intersection with calculated pageID scores that postings2 should be merged into
# 	  	 postings_2: postings list to be intersected into postings_1 -- still has raw wf's rather than idf*wf scores
#		 idf: idf of word corresponding to postings_2
#		 boolean stating whether this is for handle_PQ or handle_BQ:
#			False (handle_BQ): is passed as 0 and means this is for the BQ_AND and there should be no further call to positional_AND
#			True (handle_PQ): means any other value, which is passed in as the difference of the indecies of query1 and query2, for the sake of the positional_AND.
#				--> If true, function uses helper procedure positional_AND 
#		if true: returns the intersection over the pageID's
#		if false: returns the intersection over the pageID's and positions (where position_2 directly after position_1)
def postings_AND(postings_1, postings_2, idf, i_difference):
	intersection = []  # Even if just matching PageID's, I want this to still be a full postings list rather than just pageIDs so that we can iterate on this function with ease
	pageIndex_1 = 0
	pageIndex_2 = 0
	length_1 = len(postings_1)
	length_2 = len(postings_2)
	# instead of storing skip pointers, we use skip pointers by just indexing in sqrt(len(list)) ahead to check if we should skip
	skip_1 = int(sqrt(length_1)) # precalculated skip for postings_1
	skip_2 = int(sqrt(length_2)) # precalculated skip for postings_2

	while (pageIndex_1 < length_1) and (pageIndex_2 < length_2):
		(pageID_1, score_1, positions_1) = postings_1[pageIndex_1]
		(pageID_2, wf_2, positions_2) = postings_2[pageIndex_2]

		if pageID_1 == pageID_2: # pageID's match!
			score = score_1 + (idf*wf_2)
			if not i_difference: 
				# we're just ANDing over pageIDs so we reached a match -- keep that post since it belongs in intersection
				intersection.append([pageID_1, score, positions_1]) # update score, positions irrelevant
			else: 
				# we're also matching positions, so keep checking for match in positions
				position_intersection = positions_AND(positions_1, positions_2, i_difference) # take intersection of positions lists
				# only append to intersection if positions_intersection is a nonempty list
				if position_intersection:
					intersection.append([pageID_1, score, position_intersection]) 
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

# helper to handle_PQ -- handles the AND & uses helper function postings_AND
# input: postings_1: current intersection with calculated pageID scores that postings2 should be merged into
# 	  	 postings_2: postings list to be intersected into postings_1 -- still has raw wf's rather than idf*wf scores
#		 idf: idf of word corresponding to postings_2
# 		 takes as 4th parameter: difference in indecies of words in query that correspond to the postings.  This is for the purpose of the positional ANDing
#				(each entry (pageID, position) in postings_1 that appears in intersection, has a corresponding entry (pageID, position+i_difference) that appears in postings_2)
# output: intersection with updated scores
def PQ_AND(postings_1, postings_2, idf, i_difference):
	return postings_AND(postings_1, postings_2, idf, i_difference)

# helper to handle_BQ -- handles the AND & uses helper function postings_AND
# input: postings_1: current intersection with calculated pageID scores that postings2 should be merged into
# 	  	 postings_2: postings list to be intersected into postings_1 -- still has raw wf's rather than idf*wf scores
#		 idf: idf of word corresponding to postings_2
# output: intersection with updated scores
def BQ_AND(postings_1, postings_2, idf):
	return postings_AND(postings_1, postings_2, idf, 0)


# input: postings1: postings list to merge second postings list into -- its posts already have correctly calculated scores for documents
#		 postings2: postings list to merge into postings1
#		 idf: inverse document frequency of term corresponding to postings2
# output: union of postings1 and postings2 where each item is a tuple (pageID, updated weight, [positions list])
def postings_OR(postings_1, postings_2, idf):
	union = [] # I want this to still be a full postings list rather than just pageIDs so that we can continue to utilize skip-pointers in further iterations
	i_1 = 0
	i_2 = 0
	while 1:
		# check if we're at the end of one of the postings lists
		if i_1 == len(postings_1):
			# tack on the rest of the postings_2 (after wf's converted to idf.wf doc scores) to union and we're done
			while i_2 < len(postings_2):
				post_2 = postings_2[i_2]
				post_2[1] *= idf # score = idf*wf
				union.append(post_2)
				i_2 += 1
			break

		if i_2 == len(postings_2):
			# tack on the rest of the postings_1 to union and we're done -- we already know that it has correctly calculated document scores
			while i_1 < len(postings_1):
				union.append(postings_1[i_1])
				i_1 += 1
			break
		# verified we're not at the end of one of the postings lists
		post_1 = postings_1[i_1]
		post_2 = postings_2[i_2]  # looks like (pageID, wf, [positions])
		pageID_1 = post_1[0]
		pageID_2 = post_2[0]

		toAdd = idf*post_2[1] # idf*wf
		
		if pageID_1 == pageID_2:
			post_1[1] += toAdd
			union.append(post_1)
			i_1 += 1
			i_2 += 1
		elif pageID_1 < pageID_2:
			union.append(post_1)
			i_1 += 1
		else: #pageID_1 > pageID_2
			post_2[1] = toAdd
			union.append(post_2)
			i_2 += 1

	return union

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 boolean expression (expr) -- that this function is called recursively on
# output: tuple (postings-list, idf): postings-list that satisfies boolean expression (expr)
def handle_BQ_expr(stopwords_set, index, stemmer, expr, N):
	# base case
	if type(expr) == str:
		token = tokenize(stopwords_set, stemmer, expr, False)[0]
		if token in index:
			(df, postings) = index[token]
			idf = log((N/df),2)
			return (postings, idf)
		else:
			return ([], 1)
	else:
		operator = expr[0] # AND or OR
		arguments = expr[1] # list of boolean expressions (base case is that they're just words)
		base_postings = []

		if operator == 'OR':
			for arg in arguments:
				(postings, idf) = handle_BQ_expr(stopwords_set, index, stemmer, arg, N)
				base_postings = postings_OR(base_postings, postings, idf) 
			return (base_postings, 1)
		else: # operator == 'AND'
			heap = [] # want to first sort arguments postings by length so we can being ANDing with smallest list
			for arg in arguments:
				(postings, idf) = handle_BQ_expr(stopwords_set, index, stemmer, arg, N)
				heapq.heappush(heap, (len(postings), (idf, postings)))

			(idf, base_postings) = heapq.heappop(heap)[1]
			heap_len = len(heap)
			for j in range(len(heap)):
				(idf, postings) = heapq.heappop(heap)[1]
				base_postings = BQ_AND(base_postings, postings, idf)
			return (base_postings, 1)
			 
# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
#		 total documents (N)  --- necessary to compute idf
def handle_BQ(stopwords_set, index, stemmer, query, N):
	# ('OR', ['Her', ('OR', ['This', 'That']), ('OR', ['This', 'That'])])
	# for now we assume we get well formed Boolean queries with no stopwords
	bool_expr = bool_parse(query)
	(postings, idf) = handle_BQ_expr(stopwords_set, index, stemmer, bool_expr, N)
	return postings

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
#		 total documents (N)  --- necessary to compute idf
# output: list of posts of the matching documents in order of pageID
# 			for PQ matching documents contain subsequence [t1, t2, .., tk] in this order with adjacent terms
def handle_PQ(stopwords_set, index, stemmer, query, N):
	# obtain stream of terms from query -- also handles removing operators "" and newline '\n'
	stream_list = tokenize(stopwords_set, stemmer, query, True)
	# initialize variables in greater scope
	intersection = []
	tup = None

	heap = [] # I use a heap to first sort out which postings lists are smallest -- so that my ANDing can be efficient
	for i in range(len(stream_list)):
		word = stream_list[i]
		if not word in index: 
			# word isn't in index, so we can satisfy positional query -- return no documents
			return []
		else:
			# otherwise, store postings in heap, where heap sorts by length of postings.  Also need to store index of work in query for the positional AND
			(df, postings) = index[word]
			idf = log((N/df),2)
			tup = (len(postings), (i, postings, idf)) # stores in heap: (len(postings), (indexInQuery, idf, postings))
			heapq.heappush(heap, tup)

	num_tokens = len(heap)
	i_1 = 0
	i_2 = 0
	if not num_tokens:
		return [] # returns empty list
	else:
		tup = heapq.heappop(heap) # tup = (len(postings), (indexInQuery, idf, postings))
		(i_1, idf, postings) = tup[1]
		# get inital intersection
		intersection = updateScores(postings, idf) # update scores takes normal postings list and multiplies each wf by idf to get score

	for j in range(1, num_tokens):
		tup = heapq.heappop(heap) # tup = (len(postings), (indexInQuery, idf, postings))
		(i_2, idf, postings) = tup[1]
		# update intersection by intersecting on current intersection, and newly retrieved postings list.  
		intersection = PQ_AND(intersection, postings, idf, i_2-i_1) # We send in the difference of the indecies of the words in query for the positional AND
		if not intersection:
			# if nothing is left in intersection, can break out of loop now with nothing to return
			return []
		else:
			i_1 = i_2 # otherwise update our indecies for the purpose of the parameters for positional AND

	return intersection



# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
#		 total documents (N)  --- necessary to compute idf
# output: lists of posts of matching documents in order of pageID
# 			for FTQ matching documents contain at least one word whose stemmed version is one of the ti's
def handle_FTQ(stopwords_set, index, stemmer, query, N):
	# turn query into stream of tokens
	stream_list = tokenize(stopwords_set, stemmer, query, True)
	stream_length = len(stream_list)
	if not stream_length: # make sure we got some tokens out of that query
		return []
	# initialize union to empty list
	union = []

	for i in range(stream_length):
		term = stream_list[i]
		if term in index:
			(df, postings) = index[term]
			idf = log((N/df),2)
			union = postings_OR(union, postings, idf)
	return union
 

# input: set of stopwords (stopwords_set)
#		 inverted index (index)
#		 porter stemmer (stemmer)
# 		 query (query) -- from which we obtain list of stream of words (stream_list) [t0, t1, t2, ..., tk]
#		 total documents (N)  --- necessary to compute idf
# helper routine to queryIndex -- determines type of query and passes off to further handling
def handle_query(stopwords_set, index, stemmer, query, N):
	# determine query type (OWQ, FTQ, PQ, BQ)
	if ('AND' in query or 'OR' in query or ')' in query or '(' in query):  # note that the boolean parser strips off trailing '\n'
		# handle BQ in its own way
		return handle_BQ(stopwords_set, index, stemmer, query, N)
	
	if (query[0]=='"' and query[len(query)-2]=='"' and query[len(query)-1]=='\n') or (query[0]=='"' and query[len(query)-1]=='"'): # it's a PQ
		return handle_PQ(stopwords_set, index, stemmer, query, N)
		
	else: # it's a OWQ or FTQ
		return handle_FTQ(stopwords_set, index, stemmer, query, N)

# helper to queryIndex main function that sorts the posts retrieved
# creates a max-heap -- stuffs all the posts into the heap, and then pops them off and puts the pageID in string form
# input: list of posts sorted by pageID
# output: string of pageIDs sorted by document score
def sort_posts(posts):
	heap = []
	for j in range(len(posts)):
		tup = posts[j] # (pageID, score, [positions list])
		heapq.heappush(heap, ((-1)*tup[1], str(tup[0]))) # push to heap: (pageID, -score) -- using (-score) to turn minheap to maxheap
	
	documents = ''
	count = 0
	for i in range(14):
	#while 1:
		if len(heap) == 0:
			break
		if count > 0:
			documents += ' '
		count += 1
		next = heapq.heappop(heap)
		#documents += next[1]
		documents += ("("+next[1]+","+str(-1*next[0])+")")
	return documents

# main function
def queryIndex(stopwords_filename, ii_filename, ti_filename):
	# rebuild index from file, and minipulate it into a permuterm index for wildcard queries.  Rebuild stopwords set from file
	(index,N) = reconstruct_Index(ii_filename)
	permutermIndex = permutermIndex(index) 
	stopwords_set = create_stopwords_set(stopwords_filename)
	# instantiate stemmer to pass into tokenize
	stemmer = PorterStemmer()
	#print("ready..")
	while 1: # read queries from standard input until user enters CTRL+D
		try:
			query = sys.stdin.readline()
		except KeyboardInterrupt:
			break
		if not query:
			break
		posts = handle_query(stopwords_set, index, stemmer, query, N)
		documents = sort_posts(posts)
		print(documents)
	return	

queryIndex(sys.argv[1], sys.argv[2], sys.argv[3])

