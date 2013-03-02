# file that minipulates loaded dictionary into a permuterm index btree --- deals with the handling of WildCard queries
from BTrees.OOBTree import OOBTree


# example: 
# therange = t.keys(min='c', max='d', excludemin=False, excludemax=True)
# for i in therange:


# creates permuterm index from dictionary index to aid with wildcard queries
# input: dictionary (index)
# output: permuterm-index in btree data structure (permutermIndex)
def permutermIndex(index):
	tree = OOBTree()
	for term in index:  #'hello'
		term += '$'		# 'hello$'
		for i in range(len(term)-1):
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
	stars = 0 # for now counting the stars -- expect: 0 < stars <= 2 
	length = len(term)

	end = ''
	middle = ''
	front = ''
	curr = front

	for i in range(len(term)):
		ch = term[i]
		if ch == '*':
			stars += 1
			if stars == 1:
				curr = end
			elif stars == 2:
				middle = end
				end = ''
			else: # more stars than expected: error
				print("To many ("+str(stars)+") **************************")
				return {}
		else:
			curr += ch
	end += '$'
	seek = end+front

	
























