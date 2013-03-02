# queryIndex util


# helps out the handle_PQ, -- for the first postings list in the intersection, need to convert wf's into idf*wf scores right away
# input: postings list of format [[pageID, wf, [positions]] for each pageID]
# output: postings list of format [[pageID, score(idf,wf), [positions]] for each pageID]
def updateScores(postings, idf):
	for post in postings:
		post[1] *= idf
	return postings 
