import sys
import os
os.chdir(os.path.abspath(os.path.dirname(__file__)))
import doctest
import unittest
from difflib import SequenceMatcher
from misc import normalizeStr, average
import sitescraper as ss
from data import *


# change to fold testing
def runExampleData():
    modelSize = 3
    os.chdir('data')
    accuracies = []
    for site, d in sorted(data.items())[-2:-1]:
        model = ss.trainModel(d[:modelSize])
        print site, 'model:', model
        for url, expectedOutput in d:
            print url
            generatedOutput = ss.testModel(url, model)
            #print generatedOutput
            for i, e in enumerate(expectedOutput):
                e = normalizeStr(e)
                s = SequenceMatcher()
                s.set_seq2(e)
                genLCSs = [(0, '')]
                for g in generatedOutput:
                    g = normalizeStr(g)
                    s.set_seq1(g)
                    genLCSs.append((sum(n for (i, j, n) in s.get_matching_blocks()), g))
                thisLCS, g = max(genLCSs)
                """if i < len(generatedOutput):
                    g = normalizeStr(generatedOutput[i])
                else:
                    g = ''

                s = SequenceMatcher(None, e, g)
                thisLCS = sum(n for (i, j, n) in s.get_matching_blocks())"""
                maxLCS = len(e)
                accuracies.append(100 * thisLCS // maxLCS)
                if thisLCS < 0.99*maxLCS:
                    print '%d/%d (%d%%)' % (thisLCS, maxLCS, accuracies[-1])
                    #continue
                    print 'Expected:',
                    print e
                    print 'Get:     ',
                    print g
                    print
                else:
                    pass # success!
    print "Accuracy: %.2f%%" % average(accuracies)


def runDocTests():
    suite = unittest.TestSuite()
    for mod in ['sitescraper', 'misc']:
        suite.addTest(doctest.DocTestSuite(__import__(mod)))
    runner = unittest.TextTestRunner()
    runner.run(suite)



if __name__ == '__main__':
    args = sys.argv[1:]
    if 'data' in args:
        runExampleData()
    elif 'doc' in args:
        runDocTests()
    else:
        print('Usage: python %s data|doc' % sys.argv[0])