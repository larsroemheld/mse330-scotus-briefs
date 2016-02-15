

import os
import pprint as pp
import re
import logging
import loadDocketInfo
from collections import Counter
import itertools
import re

import matplotlib.pyplot as plt

amicus_re = re.compile('amicus')
tau_re = re.compile('TABLE\s+OF\s+AUTHORITIES', re.IGNORECASE)
files = os.listdir("../textified")


num_amicus_files = 0
sparse_files = []
successful_files = []
files_not_found = []

file_lengths = []

for fn in files:
    match = amicus_re.search(fn)
    if match is None:
        continue

    num_amicus_files += 1

    with open("../textified/" + fn) as f:
        num_lines = 0
        found = False
        for line in f:
            num_lines += 1
            tau_match = tau_re.search(line)
            if tau_match is not None:
                found = True

        if not found:
            if num_lines == 0:
                sparse_files.append(fn)
            else:
                file_lengths.append(num_lines)
                files_not_found.append(fn)
        else:
            file_lengths.append(num_lines)
            successful_files.append(fn)

print "Number of Successful A.B. (found a table of authorities string): {}".format(len(successful_files))
print "Number of Empty A.B.: {}".format(len(sparse_files))
print "Total Number of Amicus Briefs: {}".format(num_amicus_files)

print "What follows are the filenames of the unsuccessful cases"
pp.pprint(files_not_found)

plt.hist(file_lengths)
plt.show()


# Example of the formatting issues that might be throwing us off 
a = "OT 2011_11-400_amicus briefs27.txt"
with open("../textified/" + a) as f:
    found = False
    for line in f:
        tau_match = tau_re.search(line)
        if tau_match is not None:
            found = True
        print "found: {} | {}".format(found, line)

