

import re
import os
import pprint as pp
from bs4 import BeautifulSoup
import sys
sys.setrecursionlimit(10000)


dirname = "reports"
test_filename = "OT 2007_06-179_opinion.txt.OT 2007_06-179_amicus briefs5.html"
filenames = os.listdir(dirname)

opinion_re = re.compile(r'^([\w\s\_\-]+)_opinion.txt')


filenames = filter(lambda x: opinion_re.search(x), filenames)

for target_file in filenames:
    full_path = os.path.abspath(os.path.join(dirname, target_file))

    meta = []
    match = re.search(r'^([\w\s\_\-]+)_opinion\.txt.+_(amicus briefs.+)\.html', target_file)
    if match:
        meta.append(match.group(1))
        meta.append(match.group(2))
    else:
        assert(false) # should really throw an exception, but going fast right now

    f = open(full_path)
    html_doc = f.read()
    f.close()
    soup = BeautifulSoup(html_doc, 'html.parser')
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        pl_text = a_tag.find_all(text=True)
        pl_text = [x.encode('UTF8').strip() for x in pl_text]
        pl_text = ' '.join(pl_text)
        print ",".join(meta) + "," + pl_text

    
    
    






