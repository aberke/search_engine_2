# all the helpers for BQ

from math import sqrt# used for calculating skip pointers
import heapq # using heap to sort postings lists by length so we can begin ANDing with smallest list

from queryIndex_util import initial_postings_scores, index_postings, df_to_idf
from XMLparser import tokenize




# helper to handle_BQ -- handles the AND & uses helper function postings_AND
# input: postings_1: current intersection with calculated pageID scores that postings2 should be merged into
# 	  	 postings_2: postings list to be intersected into postings_1 -- still has raw wf's rather than idf*wf scores
#		 scores: dictionary mapping pageID to document score
# output: tuple (intersection, scores) where scores is updated from input
def BQ_AND(postings_1, postings_2, scores):
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
			if not pageID_1 in scores: ###
				print('&&&&&&&& PAGEID NOT ALREADY IN SCORES')
			# we're just ANDing over pageIDs so we reached a match -- keep that post since it belongs in intersection
			intersection.append([pageID_1, 0, positions_1]) # update score, positions irrelevant
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
	return (intersection, scores)


# input: postings1: postings list to merge second postings list into -- its posts already have correctly calculated scores for documents
#		 postings2: postings list to merge into postings1
#		 scores: dictionary mapping pageID to document scores
# output: union of postings1 and postings2 where each item is a tuple (pageID, wf, [positions list])
def BQ_OR(postings_1, postings_2, scores):
	union = [] # I want this to still be a full postings list rather than just pageIDs so that we can continue to utilize skip-pointers in further iterations
	i_1 = 0
	i_2 = 0
	while 1:
		# check if we're at the end of one of the postings lists
		if i_1 == len(postings_1):
			# tack on the rest of the postings_2 (after wf's converted to idf.wf doc scores) to union and we're done
			while i_2 < len(postings_2):
				(pageID, wf, positions) = postings_2[i_2] # copy it rather than point to it so that we can mess with score
				if not pageID in scores: ###
					print('PAGEID NOT IN SCORES ALREADY IN BQ_OR')
				###score = idf*wf
				###union.append([pageID, score, positions])
				union.append([pageID, wf, positions])
				i_2 += 1
			break

		if i_2 == len(postings_2):
			# tack on the rest of the postings_1 to union and we're done -- we already know that it has correctly calculated document scores
			while i_1 < len(postings_1):
				if not postings_1[i_1][0] in scores: ###
					print('PAGEID NOT IN SCORES ALREADY IN BQ_OR')
				union.append(list(postings_1[i_1])) # copy it rather than point to it so we can mess with score
				i_1 += 1
			break
		# verified we're not at the end of one of the postings lists
		(pageID_1, score_1, positions_1) = postings_1[i_1]
		(pageID_2, wf_2, positions_2) = postings_2[i_2]

		if pageID_1 == pageID_2:
			if not pageID_1 in scores: ###
				print('PAGEID NOT IN SCORES ALREADY IN BQ_OR')			
			###
			###score = score_1 + (idf*wf_2)
			###union.append([pageID_1, score, positions_1])
			union.append([pageID_1, score_1, positions_1])
			i_1 += 1
			i_2 += 1
		elif pageID_1 < pageID_2:
			if not pageID_1 in scores: ###
				print('PAGEID NOT IN SCORES ALREADY IN BQ_OR')
			union.append([pageID_1, score_1, positions_1])
			i_1 += 1
		else: #pageID_1 > pageID_2
			if not pageID_2 in scores: ###
				print('PAGEID NOT IN SCORES ALREADY IN BQ_OR')
			###union.append([pageID_2, idf*wf_2, positions_2])
			union.append([pageID_2, wf_2, positions_2])
			i_2 += 1
	return (union, scores)
