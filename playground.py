__author__ = 'lars'

import logging
import loadDocketInfo
from collections import Counter

cases = loadDocketInfo.loadCases('cases.json')
print 'Loaded {0} cases.'.format(str(len(cases)))

word_counter = Counter()
for c in cases:
    n = len(c['documents'])
    for i in range(n):
        fn = loadDocketInfo.getCaseDocFilename(c, i)
        try:
            with open('textified/' + fn, 'r') as f:
                for line in f:
                    for word in line.split():
                        word_counter[word.lower()] += 1
        except:
            logging.error('Could not open file {0} (download error?), continuing.'.format(fn))

for (w, c) in word_counter.most_common(100):
    print "{0} instances: {1}".format(c, w)
