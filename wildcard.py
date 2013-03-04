# file that minipulates loaded dictionary into a permuterm index btree --- deals with the handling of WildCard queries
from BTrees.OOBTree import OOBTree

# takes in term that has been rotated around the $ at the end of term -- want to get back orinal term
# input: rotated permuterm index term from which we want to retrieve real word -- ie input may be 'llo$he'
# output: word represented by rotated term -- ie if input is 'llo$he' then should return 'hello'
def unrotateTerm(term):
	term = term.split('$')
	return term[1]+term[0]


# creates permuterm index from dictionary index to aid with wildcard queries
# input: dictionary (index)
# output: permuterm-index in btree data structure (permutermIndex)
def permutermIndex_create(index):
	tree = OOBTree()
	for term in index:  #'hello'
		term += '$'		# 'hello$'
		for i in range(len(term)):
			tree[term] = True
			term = term[1:]+term[0]
	return tree

# input: wildcard query
# output: set of terms matching wildcard query
#
# can assume each wildcard word contains at most two *'s and that they will not be contiguous (ie, may have lol*t* but never strangel**ve)
# Consider the wildcard query m*n. 
#	Rotate wildcard query st * appears at end of string - rotated wildcard query becomes n$m*. L
#	Look up this string in the permuterm index, where seeking n$m* (via a search tree) leads to rotations of (among others) the terms man and moron
def wildcard(tree, term):
	results = {}
	# rotate word
	end = ''
	middle = ''
	front = ''
	term = term.split("*") #expect: 0 < stars = len(term)-1 <= 2 
	
	if len(term) == 1:
		return {term[0]:True}
	elif len(term) == 2:
		front = term[0]
		end = term[1] + '$'
	elif len(term) == 3:
		front = term[0]
		middle = term[1]
		end = term[2] + '$'
	else:
		print("ERROR IN WILDCARD -- TOO MANY **************** IN QUERY")
		return results

	seek = end+front
	seekMax = seek[:len(seek)-1]+chr(ord(seek[len(seek)-1])+1)
	# get results
	theRange = tree.keys(min=seek, max=seekMax, excludemin=False, excludemax=True)
	#items_count = 0
	for t in theRange:
		if middle in t:
			# found a match! but need to rotate it back into an actual term
			#results[items_count] = unrotateTerm(t)
			#items_count += 1
			results[unrotateTerm(t)] = True
	return results




