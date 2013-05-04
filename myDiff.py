import sys


# print out document IDs that messed up in matching, with how many times that was not a match
def problematic_docs(myDoc1, expected1, myDoc2, expected2):
    print('starting.....')
    f1 = open(myDoc1, 'r')
    f2 = open(expected1, 'r')
    count = 0
    bad = {}
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        count += 1
        if count < 100:
            if line1 != line2:
                line1 = line1.split()
                line2 = line2.split()
                for i in range(len(line2)):
                    if line1[i] != line2[i]:
                        if line1[i] not in bad:
                            bad[line1[i]] = 0
                        bad[line1[i]] += 1
        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close() 
    # do the same with the next set of documents
    f1 = open(myDoc2, 'r')
    f2 = open(expected2, 'r')
    count = 0
    bad = {}
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        count += 1
        if count < 100:
            if line1 != line2:
                line1 = line1.split()
                line2 = line2.split()
                for i in range(len(line2)):
                    if line1[i] != line2[i]:
                        if line1[i] not in bad:
                            bad[line1[i]] = 0
                        bad[line1[i]] += 1
        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()
    for badDoc in bad:
        if bad[badDoc] > 1:
            print(str(badDoc)+': '+str(bad[badDoc]))





def thisLine(fname1, fname2, line):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    while count < line:
        line2 = f2.readline()
        count += 1
    while line1 or line2:
        line1 = line1.split()
        line2 = line2.split()
        count += 1
        if count < 2:
            if line1[:10] != line2:
                print("********************************")
                print('lines '+str(count)+' dont match')
                print('file1 has:')
                print(line1)
                print('file2 has:')
                print(line2)
                print("********************************")

        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()   

# input: fname1 is a scores file 
def compare_scores(fname1, fname2):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        if line1[len(line1)-1] == '\n':
            line1 = line1[:len(line1)-1]
        count += 1
        #print("count: "+str(count))
        if not line1:
            if line2 != '\n':
                print("********************************")
                print('lines '+str(count)+' dont match')
                print("line1 empty")
                print("line2: "+line2)
                print("********************************")

        elif count < 100:
            line2 = line2.split()
            line1 = line1.split(') (')
            line1IDs = []
            line1scores = []
            for i in range(len(line1)):
                tup = line1[i].split(',')
                line1IDs += [tup[0]]
                line1scores += [tup[1]]
            if line1IDs != line2:
                print("********************************")
                print('lines '+str(count)+' dont match')
                has1 = 'file1 has '+str(len(line1IDs))+': '
                has2 = 'file2 has '+str(len(line2))+': '
                for i in range(len(line1IDs)):
                    if i>= len(line2):
                        has1 = has1 + " <<"+line1IDs[i]+  "|"+line1scores[i]+">>"
                    elif line1IDs[i] != line2[i]:
                        has1 = has1 + " <<"+line1IDs[i]+  "|"+line1scores[i]+">>"
                        has2 = has2 + " <<"+line2[i]+">>               "
                    # else:
                    #     has1 = has1 + " "+line1IDs[i]
                    #     has2 = has2 + " "+line2[i]
                    else:
                         has1 = has1 + " ("+line1IDs[i]+  "|"+line1scores[i]+")"
                         has2 = has2 + " ("+line2[i]+")              "             
                print(has1)
                print(has2)                  
                print("********************************")

        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()

def compare(fname1, fname2):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        count += 1
        if count < 100:
            if line1 != line2:
                line1 = line1.split()
                line2 = line2.split()
                print("********************************")
                print('lines '+str(count)+' dont match')
                has1 = 'file1 has '+str(len(line1))+': '
                has2 = 'file2 has '+str(len(line2))+': '
                for i in range(len(line2)):
                    if line1[i] != line2[i]:
                        has1 = has1 + " <<|| "+line1[i]+" ||>>"
                        has2 = has2 + " <<|| "+line2[i]+" ||>>"
                    else:
                        has1 = has1 + " "+line1[i]
                        has2 = has2 + " "+line2[i]
                print(has1)
                print(has2)                  
                print("********************************")

        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()

def thisDiff(fname1, fname2):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        line1 = line1.split()
        line2 = line2.split()
        count += 1
        if line1 != line2:
            print("********************************")
            print('lines '+str(count)+' dont match')
            i2 = 0
            doc2_has = ''
            while i2 < len(line2):
                doc2 = line2[i2]
                if not doc2 in line1:
                    doc2_has += doc2 + ' '
                i2 += 1
            print('file2 had items that file1 didnt have:')
            print(doc2_has)
            print("********************************")

        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()

def thatDiff(fname1, fname2):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        line1 = line1.split()
        line2 = line2.split()
        count += 1
        if line1 != line2:
            print("********************************")
            print('lines '+str(count)+' dont match')
            i1 = 0
            i2 = 0
            doc1_has = ''
            doc2_has = ''
            while i1 < len(line1) and i2 < len(line2):
                doc1 = line1[i1]
                doc2 = line2[i2]
                if doc1 < doc2:
                    doc1_has += doc1 + ' '
                    i1 += 1
                elif doc1 > doc2:
                    doc2_has += doc2 + ' '
                    i2 += 1
                else:
                    i1 += 1
                    i2 += 1
            while i1 < len(line1):
                doc1_has += line1[i1] + ' '
                i1 += 1
            while i2 < len(line2):
                doc2_has += line2[i2] + ' '
                i2 += 1
            print('file1 had items that file2 didnt have:')
            print(doc1_has)
            print('file2 had items that file1 didnt have:')
            print(doc2_has)
            print("********************************")

        line1 = f1.readline()
        line2 = f2.readline()
    f1.close()
    f2.close()

#problematic_docs(sys.argv[1], sys.argv[2],sys.argv[3], sys.argv[4])
#compare_scores(sys.argv[1], sys.argv[2])
compare(sys.argv[1], sys.argv[2])
#thisDiff(sys.argv[1], sys.argv[2])
#thatDiff(sys.argv[1], sys.argv[2])
