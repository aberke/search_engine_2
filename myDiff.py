import sys


def compare(fname1, fname2):
    print('starting.....')
    f1 = open(fname1, 'r')
    f2 = open(fname2, 'r')
    count = 0
    line1 = f1.readline()
    line2 = f2.readline()
    while line1 or line2:
        # if count >= 1:
        #     break
        line1 = line1.split()
        line2 = line2.split()
        count += 1
        if count == 19:
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


compare(sys.argv[1], sys.argv[2])
#thisDiff(sys.argv[1], sys.argv[2])
#thatDiff(sys.argv[1], sys.argv[2])