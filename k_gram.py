
import logging
import loadDocketInfo
from collections import Counter
import pprint as pp
import itertools
import re
import unicodedata

# Parameters
case_info = "../cases.json"
k = 8
# pattern = re.compile('\xd3') # not currently used
r_pattern = re.compile(r'[\w]')

### HELPER FUNCTIONS ###

# http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
# Helper function that returns a list of
def find_kgrams(input_list, k):
    assert(len(input_list) >= k)
    return itertools.izip(*[input_list[i:] for i in xrange(k)])


# Our criterion for keeping a word 
def word_filter(input_string):

    # Discard any that don't even have one alphanumeric 
    match = r_pattern.search(input_string)
    if match is None:
        return False

    # Controversial methinks: might be a good indicator of science
    # But I keep on getting things like 8->9->10->11
    # Somehow this breaks it? Maybe unicode always returns numeric or something?
    '''
    if input_string.isnumeric():
        return False
    '''

    if input_string == ".": 
        return False

    return True

cases = loadDocketInfo.loadCases(case_info)
print 'Loaded {0} cases.'.format(str(len(cases)))

case_document_counts = Counter()
case_missed_counts = Counter()
k_gram_counters = Counter()
for number, case in enumerate(cases):
    logging.error(number)
    # print number # Just for me to see how fast it's going
    case_identifier = case["Term"] + " " + case["Docket No."] # same format as the input files
    n = len(case['documents'])
    case_document_counts[case_identifier] = n

    for i in range(n):
        fn = loadDocketInfo.getCaseDocFilename(case, i)

        try:
            with open('../textified/' + fn, 'r') as f:
                for line in f:

                    # Preprocessing
                    words = line.split()
                    filtered_words = list(filter(lambda x: word_filter(x), words))

                    # Find k-grams
                    if len(filtered_words) < k: continue
                    k_grams = find_kgrams(filtered_words, k)
                    for gram in k_grams:
                        k_gram_counters[gram] += 1

        except:
            case_missed_counts[case_identifier] += 1 
            logging.error('    Could not open file {0} (download error?), continuing.'.format(fn))

total_num_successful = 0
for (case_identifier, count) in case_document_counts.most_common():
    num_successful = count - case_missed_counts[case_identifier]
    total_num_successful += num_successful
    print "{}: {}/{} were successful".format(case_identifier, num_successful, count)

for (kgram, count) in k_gram_counters.most_common(25000):
    string_form = "->".join(kgram)
    print "{} instances: {}".format(count, string_form)














