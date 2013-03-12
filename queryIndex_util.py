# queryIndex util
import heapq # using heap to sort postings lists by length so we can begin ANDing with smallest list
from math import log # used for calculating inverse document frequency (idf)

from wildcard import wildcard


# heper to sort_posts and sort_posts_BQ --> does the popping of the heap
# input: heap (heap) where elements are lists [-score, -pageID, pageID]
# output: string (sorted_documents) that is the pageIDs sorted by document score
def sort_posts_pop(heap):
	documents = ''
	for i in range(10):
		if len(heap) == 0:
			break
		next = heapq.heappop(heap) # next = entry [-score, -pageID, str(pageID)]
		if i > 0:
			#documents += ") ("
			documents += ' '
		documents += next[2]
		#documents = documents +next[2]+","+str(-1*next[0])
	return documents


# helper to queryIndex main function that sorts the posts retrieved -- specific for BQ queries since scoring done in separate dictionary
# creates a max-heap -- stuffs all the posts into the heap, and then pops them off and puts the pageID in string form
# input: list of posts sorted by pageID (posts)
#		 dictionary mapping pageID's to scores (scores)
# output: string of pageIDs sorted by document score
def sort_posts_BQ(posts, scores):
	heap = []
	# when documents have the same score I want to order them in the same order as the TA's -- convention seems that when 2 docIDs match, TAs order larger docID first
	for j in range(len(posts)):
		pageID = posts[j][0] # (pageID, score, [positions list])
		score = round(scores[pageID], 4) # it seems like they're using about this level of precision... let's see
		# push to heap: [-score, -pageID, pageID] -- using (-)*score to turn minheap to maxheap and using (-1)*pageID in case same score and higher pageID should be first
		entry = [(-1)*score, (-1)*pageID, str(pageID)]
		heapq.heappush(heap, entry) 
	
	sorted_documents = sort_posts_pop(heap)
	return sorted_documents

# helper to queryIndex main function that sorts the posts retrieved
# creates a max-heap -- stuffs all the posts into the heap, and then pops them off and puts the pageID in string form
# input: list of posts sorted by pageID
# output: string of pageIDs sorted by document score
def sort_posts(posts):
	heap = []
	# when documents have the same score I want to order them in the same order as the TA's -- convention seems that when 2 docIDs match, TAs order larger docID first
	for j in range(len(posts)):
		tup = posts[j] # (pageID, score, [positions list])
		score = round(tup[1], 4) # it seems like they're using about this level of precision... let's see
		# push to heap: [-score, -pageID, pageID] -- using (-)*score to turn minheap to maxheap and using (-1)*pageID in case same score and higher pageID should be first
		entry = [(-1)*score, (-1)*tup[0], str(tup[0])]
		heapq.heappush(heap, entry) 
	
	sorted_documents = sort_posts_pop(heap)
	return sorted_documents



def print_term_data(N, index, term):
	data = 'total docs: '+str(N)+', term: '+term+', term df: '
	if not term in index:
		data += 'term not in index!'
	else:
		data += str(index[term][0])
	print(data)


# computes idf from df and N (total documents) -- made this helper function so there would be no difference in computation style anywhere
def df_to_idf(N, df): 
	return log(float(N)/float(df)) 

# helps out the handle_BQ_expr, -- for the first postings list in the intersection, need to convert wf's into idf*wf scores right away to store in scores dictionary
# input: postings list of format [[pageID, wf, [positions]] for each pageID] (postings)
#		 idf to multiply each wf by (idf)
#		 current scores dictionary to update (scores)
# output: tuple(postings, scores): postings list of format [[pageID, score(idf,wf), [positions]] for each pageID], scores updated scores dictionary
def initial_postings_scores(postings, idf, scores):
	for post in postings:
		pageID = post[0]
		if pageID in scores:
			scores[pageID] += idf*post[1]
		else:
			scores[pageID] = idf*post[1]
	return (postings, scores)


# helps out the handle_PQ, -- for the first postings list in the intersection, need to convert wf's into idf*wf scores right away
# input: postings list of format [[pageID, wf, [positions]] for each pageID]
# output: postings list of format [[pageID, score(idf,wf), [positions]] for each pageID]
def initial_postings(postings, idf):
	updated_postings = []
	for post in postings:
		updated_postings.append([post[0], post[1]*idf, post[2]])
	return updated_postings 



# input: 2 ordered positions lists to take the union of
# output: ordered list 
def positions_OR(positions_1, positions_2):
	union = [] 
	i_1 = 0
	i_2 = 0
	while 1:
		# check if we're at the end of one of the postings lists
		if i_1 == len(positions_1):
			# tack on the rest of the postings_2 
			while i_2 < len(positions_2):
				union.append(positions_2[i_2])
				i_2 += 1
			break

		if i_2 == len(positions_2):
			# tack on the rest of the postings_1 to union and we're done 
			while i_1 < len(positions_1):
				union.append(positions_1[i_1])
				i_1 += 1
			break
		# verified we're not at the end of one of the positions lists
		pos_1 = positions_1[i_1]
		pos_2 = positions_2[i_2]

		if pos_1 == pos_2:
			union.append(pos_1)
			i_1 += 1
			i_2 += 1
		elif pos_1 < pos_2:
			union.append(pos_1)
			i_1 += 1
		else: #pos_1 > pos_2
			union.append(pos_2)
			i_2 += 1

	return union


# input: postings list to merge second postings list into (postings_1)
#		 postings list to merge into postings_1 (postings_2)
#		 boolean (positional) where true indicates that the positions lists of the wildcard query matches should be merged -- necessary for WPQ (positional)
# output: union of postings1 and postings2 where each item is a tuple (pageID, max weight, [positions list])
def wildcard_postings_merge(postings_1, postings_2, positional):
	union = [] # I want this to still be a full postings list rather than just pageIDs so that we can continue to utilize skip-pointers in further iterations
	i_1 = 0
	i_2 = 0
	while 1:
		# check if we're at the end of one of the postings lists
		if i_1 == len(postings_1):
			# tack on the rest of the postings_2 
			while i_2 < len(postings_2):
				union.append(postings_2[i_2])
				i_2 += 1
			break

		if i_2 == len(postings_2):
			# tack on the rest of the postings_1 to union and we're done 
			while i_1 < len(postings_1):
				union.append(postings_1[i_1])
				i_1 += 1
			break
		# verified we're not at the end of one of the postings lists
		(pageID_1, wf_1, positions_1) = postings_1[i_1]
		(pageID_2, wf_2, positions_2) = postings_2[i_2]  # looks like (pageID, wf, [positions])
		wf = wf_1
		positions = []
		
		if pageID_1 == pageID_2:
			if wf_2 > wf_1: # set pageID weight as the maximum
				wf = wf_2
			if positional: # take union of positions list as the new positions list
				positions = positions_OR(positions_1, positions_2)
			union.append([pageID_1, wf, positions])
			i_1 += 1
			i_2 += 1
		elif pageID_1 < pageID_2:
			union.append([pageID_1, wf_1, positions_1])
			i_1 += 1
		else: #pageID_1 > pageID_2
			union.append([pageID_2, wf_2, positions_2])
			i_2 += 1

	return union


# input: index (index) in format {index: [df, [postings list]] for each term}  postings list of form: [[pageID, wf, [positions list]] for each pageID]
#		 permuterm index (permutermIndex) to match wildcard queries to terms in index
#		 term (term) which may or may not be wildcard query -- need to return its corresponding postings list
#		 total documents (N)
#		 boolean (positional) where true indicates that the positions lists of the wildcard query matches should be merged -- necessary for WPQ (positional)
# output: tuple (df, postings list) where df = document frequency
def index_postings(index, permutermIndex, term, N, positional):
	postings = []
	df = N
	if not '*' in term:
		if term in index:
			(df, postings) = index[term]
	else: # term matches = T
		T = wildcard(permutermIndex, term)
		for t in T:
			if not t in index:
				print("#####ERROR -- TERM SHOULD BE IN INDEX -- ALEX FIX")
			(next_df, next_postings) = index[t]
			if next_df < df:
				df = next_df # df = min df for any t in T because want max idf
			postings = wildcard_postings_merge(postings, next_postings, positional)
	return (df, postings)

