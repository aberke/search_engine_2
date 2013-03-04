# queryIndex util
from wildcard import wildcard

# helps out the handle_PQ, -- for the first postings list in the intersection, need to convert wf's into idf*wf scores right away
# input: postings list of format [[pageID, wf, [positions]] for each pageID]
# output: postings list of format [[pageID, score(idf,wf), [positions]] for each pageID]
def updateScores(postings, idf):
	for post in postings:
		post[1] *= idf
	return postings 

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
		pos1 = positions_1[i_1]
		pos2 = positions_2[i_2]

		if pos_1 == pos_2:
			union.append(pos_1)
			i_1 += 1
			i_2 += 1
		elif pos_1 < pos2:
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
		post_1 = postings_1[i_1]
		post_2 = postings_2[i_2]  # looks like (pageID, wf, [positions])
		pageID_1 = post_1[0]
		pageID_2 = post_2[0]

		
		if pageID_1 == pageID_2:
			wf_1 = post_1[1]
			wf_2 = post_2[1]
			if wf_2 > wf_1: # set pageID weight as the maximum
				post_1[1] = wf_2
			if positional: # take union of positions list as the new positions list
				positions = positions_OR(post_1[2], post_2[2])
				post_1[2] = positions
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

# input: index (index) in format {index: [df, [postings list]] for each term}  postings list of form: [[pageID, wf, [positions list]] for each pageID]
#		 permuterm index (permutermIndex) to match wildcard queries to terms in index
#		 term (term) which may or may not be wildcard query -- need to return its corresponding postings list
#		 boolean (positional) where true indicates that the positions lists of the wildcard query matches should be merged -- necessary for WPQ (positional)
# output: tuple (df, postings list) where df = document frequency
def index_postings(index, permutermIndex, term, positional):
	postings = []
	df = 0
	if not '*' in term:
		if term in index:
			(df, postings) = index[term]
	else: # term matches = T
		T = wildcard(permutermIndex, term)
		for t in T:
			if not t in index:
				print("#####ERROR -- TERM SHOULD BE IN INDEX -- ALEX FIX")
			(next_df, next_postings) = index[t]
			if next_df > df:
				df = next_df # df = max df for any t in T
			wildcard_postings_merge(postings, next_postings, positional)
	return (df, postings)

