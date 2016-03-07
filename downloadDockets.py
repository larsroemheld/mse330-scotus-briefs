'''
Gets docket data from SCOTUSblog

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

from bs4 import BeautifulSoup
from bs4.element import NavigableString
import requests
import logging
import random
import os, sys, getopt
import json
import re
import urlparse
import time

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens. Borrowed from Django.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))
    return value
def getPageSoup(url):
    try:
        r = requests.get(url) # , headers={'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'}
        r.raise_for_status()
    except:
        logging.error('Getting page {0} failed: {1}'.format(url, sys.exc_info()[0]))
        return None

    try:
        soup = BeautifulSoup(r.text, 'html.parser')
    except:
        logging.error('Reading in the page html failed: {0} \n\n http data: {1}'.format(sys.exc_info()[0], r.text))
        return None
    return soup
def getSoupStringConcat(soupTag):
    '''
    Beautiful soup tags return their content text in the .string parameter if there is only one string child.
    Some unfortunate cases on scotus blog have more than one child-string, and this helper just concat's them.
    :param soupTag: a bs4 tag that contains one or more strings
    :return: a string containing all string children of soupTag, concatenated.
    '''
    if isinstance(soupTag, NavigableString): return soupTag.string
    result = ""
    for t in soupTag.descendants:
        if t.string is not None and isinstance(t, NavigableString): # only include NavigableStrings (work around .string default searching behavior)
            if t.parent.name != "script": # prevent reading js
                result = result + t.string
    return result

def downloadDocketInfo(scotusBlogUrl):
    '''
    Crawls a SCOTUSblog index page (e.g. http://www.scotusblog.com/case-files/terms/ot2015/) and creates a list of all
    docket data
    :param scotusBlogUrl: a SCOTUSblog index page
    :return: cases, a list of objects that contain various docket data, and most notable another list of (pdf) documents
    linked to each case. Each case has a unique 'Term' and 'Docket No.' guaranteed (which is generated if it cannot be found).
     All other data depends on successful scraping.
    '''
    def getDocumentData(soupAnchorTag, currentSection, baseUrl, i):
        '''
        Helper function that extracts all relevant document info from a beautiful soup html tag
        :param soupAnchorTag: bs4 tag that contains the <a> tag that links to a pdf
        :param currentSection:
        :return: dictionary that contains relevant data
        '''
        d = {}
        d['url'] = urlparse.urljoin(baseUrl, soupAnchorTag['href'])
        d['name_orig'] = getSoupStringConcat(soupAnchorTag)
        d['appeared_section'] = currentSection
        d['local_filename'] = currentSection + str(i) + '.pdf'
        return d
    def findSection(soupAnchorTag):
        '''
        Figures out the section that a given <a> anchor tag (bs4) is in, given a hacky heuristic that traverses the
        html tree upwards until a marker is found
        :param soupAnchorTag:
        :return:
        '''
        # This works fairly well 2007-2011. Post-2012 is todo.
        to_find = [('merit.?.brief.?', 'merits briefs'), # lowercase regex:key pairs (if regex is found, key is assigned).
                   ('merit.?.stage', 'merits briefs'),
                   ('amicus.brief.?', 'amicus briefs'),
                   ('amici', 'amicus briefs'),
                   ('certiorari.stage', 'certiorari stage'),
                   ('certiorari.filing.?', 'certiorari stage'),
                   ('petition.?.for.certiorari', 'certiorari stage'),
                   ('petition.?.for..?.?writ.of.certiorari', 'certiorari stage'),
                   ('tr\.', 'transcript'),
                   ('opinion.?.below', 'lower court opinion')]

        for (v, k) in to_find:
            if re.match(v, getSoupStringConcat(soupAnchorTag).lower()): return k

        # This is very inefficient (getting all pdf links and then traversing upwards in the tree to classify),
        # but due to erroneous syntax on scotusblog more straight-forward parsing failed
        searchPos = soupAnchorTag 
        while searchPos is not None:
            for s in searchPos.previous_siblings:
                if s.name is None: #when we hit a string
                    if s.string is None: continue
                    s_labels = s.string
                else:
                    s_labels = getSoupStringConcat(s).lower()

                for (v, k) in to_find:
                    if re.match(v, s_labels): return k
            searchPos = searchPos.parent
        return 'unknown'

    scotusSoup = getPageSoup(scotusBlogUrl)
    if scotusSoup is None: return None

    caseTables = scotusSoup.find_all(class_ = "caseindex")

    opinionDate_re = re.compile(r'Decided.*?(\d*\.\d*\.\d*)')

    cases = []
    for sect in caseTables:
        sect_cases = sect.find_all('td')
        for case in sect_cases:
            c_name_a = case.find(class_='case-title')
            c_name = c_name_a.string
            c_url = c_name_a['href']

            # get opinion date
            text = getSoupStringConcat(case)
            date = opinionDate_re.search(text)
            if date is not None:
                date = date.group(1)

            print date
            cases.append({'name': c_name, 'url': c_url, 'decided_date': date})

    # # (Debug) cases = [random.choice(cases), random.choice(cases), random.choice(cases)]
    iUnknownDocket = 1 # index for cases with unidentifiable docket no (unique index)
    iUnknownTerm = 1 # index for cases with unidentifiable term (unique index)
    for c in cases:
        caseSoup = getPageSoup(c['url'])
        docketDataTable = caseSoup.find(id='date-docket')
        labels = [th.string for th in docketDataTable.thead.find_all('th')]
        values = [getSoupStringConcat(th) for th in docketDataTable.tbody.find_all('td')]

        if len(labels) != len(values):
            logging.error('docket data did not match up!')

        for i in range(min(len(labels), len(values))):
            c[labels[i]] = values[i]

        if c.get('Docket No.') is None:
            c['Docket No.'] = "unknown-docket" + str(iUnknownDocket)
            iUnknownDocket += 1
        if c.get('Term') is None:
            c['Term'] = "unknown-term" + str(iUnknownTerm)
            iUnknownTerm += 1

        # get opinion url
        iOpinion = -1
        for i, th in enumerate(docketDataTable.thead.find_all('th')):
            if th.string == "Opinion": iOpinion = i
        if i > -1:
            opinion_td = docketDataTable.tbody.find_all('td')[iOpinion]
            c['opinion_url'] = opinion_td.find('a')['href']
        else:
            logging.error('Failed to find opinion link for docket no {0} ({1}) '.format(c['Docket No.'], c['Term']))

        # Get other document urls
        c['documents'] = []
        numDocs = 0
        for a in caseSoup.find_all('a'):
            if a.get('href') is not None and '.pdf' in a['href']:
                if 'MonthlyArgumentCal' in a['href']: continue # hacky way to avoid the regular "here" link
                currentSection = findSection(a)
                numDocs += 1
                c['documents'].append(getDocumentData(a, currentSection, c['url'], numDocs))
    # end for
    return cases

def downloadCaseDocuments(cases, baseFolder):
    nFilesDownloaded = 0
    nFilesFailed = 0
    for c in cases:
        folder = baseFolder + c['Term'] + '/' + c['Docket No.'] + '/'
        if not os.path.exists(folder): os.makedirs(folder)

        # time.sleep(1) # prevent bloomberg from blocking our scraper
        opinionSoup = getPageSoup(c['opinion_url'])
        if opinionSoup is not None:
            if 'bloomberglaw' in c['opinion_url']:
                content = opinionSoup.find(id='chunk_content')
                if content is None: content = opinionSoup.find(id='content_document')
                if content is None:
                    logging.warning('Case {0} ({1}) has an opinion link that could not be parsed properly. Downloading complete html instead'.format(c['Docket No.'], c['Term']))
                    content = opinionSoup.html
                opinion_text = getSoupStringConcat(content)
                filename = 'opinion.txt'
                try:
                    with open(folder + filename, 'wb') as f:
                        f.write(opinion_text.encode('utf8'))
                    nFilesDownloaded += 1
                except:
                    logging.error('Could not download a file: url {0} to local file {1}. Error: {2} \n\n Continuing.'.format(c['opinion_url'], filename, sys.exc_info()[0]))
                    nFilesFailed += 1
            else:
                logging.warning('Case {0} ({1}) has an opinion link that is not bloomberglaw. Parsing failed.'.format(c['Docket No.'], c['Term']))
                nFilesFailed += 1
        else:
            nFilesFailed += 1


        for d in c['documents']:
            try:
                r = requests.get(d['url'], stream=True)
                filename = d['local_filename']
                with open(folder + filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                    f.flush()
                nFilesDownloaded += 1
            except:
                logging.error('Could not download a file: url {0} to local file {1}. Error: {2} \n\n Continuing.'.format(d['url'], filename, sys.exc_info()[0]))
                nFilesFailed += 1

    return (nFilesDownloaded, nFilesFailed)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # TODO: can currently only reliably scrape documents until 2011 (inclusive)
    archiveSites = ['http://www.scotusblog.com/case-files/terms/ot' + str(y) + '/' for y in range(2007, 2012)]

    all_cases = []
    for url in archiveSites:
        logging.info('Trying to scrape url=' + url)
        new_cases = downloadDocketInfo(url)
        if new_cases is None:
            print("error! continuing...")
        else:
            all_cases += new_cases

    print("jsonified:")
    print(json.dumps(all_cases, sort_keys=True, indent=4))
    with open('cases.json', 'w') as f:
        json.dump(all_cases, f)
    print("... written to 'cases.json'.")

    print('Starting download of all documents...')
    downloadCaseDocuments(all_cases, './')
    print('Done.')
