'''
Query use of language in legal works using LexisNexis

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

# Note: brew install chromedriver (or pass the chromedriver executable path in the webdriver argument)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import os, logging, sys
import re

import loadDocketInfo

def waitUntilDriverLoaded(driver, error, nPage, timeout=120):
    # borrowed & adapted from https://github.com/stanford-bitcoin/bitcoin-twitter/blob/master/flask_selenium.py
    try:
        done = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-id="sr' + str((nPage - 1) * 10) + '"]'))
        )
    except:
        print(error)
        return

def LN_login(user, password, driver):
    try:
        driver.get('https://signin.lexisnexis.com/lnaccess/app/signin/aci/la')
        driver.find_element_by_id('userid').send_keys(user)
        driver.find_element_by_id('password').send_keys(password + Keys.RETURN)
    except:
        logging.error('Get LN login site')
        return False
    else:
        logging.info('Successfully logged in.')
    return True


def LN_query(query, driver):
    logging.info("Querying LN for: {}".format(query))
    searchBar = driver.find_element_by_id('searchTerms')
    searchBar.clear()
    searchBar.send_keys(query.decode('utf8').encode('ascii', 'ignore') + Keys.RETURN)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    file_in = sys.argv[1]
    if len(sys.argv) > 2: skip_lines = int(sys.argv[2])
    else: skip_lines = 0
    print "skipping {} lines!".format(skip_lines)

    # Note
    # export LEXISNEXIS_USER=username
    # export LEXISNEXIS_PASS=password
    LN_user = os.environ.get('LEXISNEXIS_USER')
    LN_pass = os.environ.get('LEXISNEXIS_PASS')
    if LN_pass is None or LN_pass is None:
        logging.error('Could not find LexisNexis credentials in environ variables. Aborting.')
        exit()

    driver = webdriver.Chrome()
    if not LN_login(LN_user, LN_pass, driver):
        exit()

    # ugly, but works :D
    logging.warning('Please change the search scope to "cases" only -- you have 20 seconds.')
    time.sleep(10)
    logging.warning('Please change the search scope to "cases" only -- you have 10 seconds.')
    time.sleep(10)

    cases = loadDocketInfo.loadCases('cases.json')
    cases_dates = loadDocketInfo.loadCases('cases_dateonly.json')
    for c in cases:
        for cd in cases_dates:
            if cd['url'] == c['url']:
                date = None
                try:
                    date = time.strptime(cd['decided_date'], '%m.%d.%Y')
                except:
                    date = time.strptime(cd['decided_date'], '%m.%d.%y')
                c['decided_date'] = date
    cases_dates = None
    print 'Loaded {0} cases.'.format(str(len(cases)))

    # Now go through and compare dates.
    #For date comparison: either use "Opinion" field in cases, or use OT years? Or re-scrape scotusblog, use decided date!
                # try:
                #     date = time.strptime(date.group(1), '%m.%d.%Y')
                # except:
                #     date = time.strptime(date.group(1), '%m.%d.%y')


    # get queries to look for
    words_re = re.compile(r'(OT \d*)_(.*?),(.*\.txt),(.*)$')
    matches = []
    with open(file_in) as f_matches:
        for line in f_matches:
            match = words_re.search(line)
            term = words_re.search(line).group(1)
            docket = words_re.search(line).group(2)
            brief = words_re.search(line).group(3)
            words = words_re.search(line).group(4)
            match = words.replace('"', '')
            matches.append({'term': term, 'docket': docket, 'brief': brief, 'match': match})

    for idx, obj in enumerate(matches):
        if idx < skip_lines: continue # skip through what's done already

        print '## Now on match (line) #'+str(idx)
        match_case = None
        for c in cases:
            if c['Term'] == obj['term'] and c['Docket No.'] == obj['docket']:
                match_case = c
                break
        if match_case is None:
            logging.error('Couldnt locate case {} in term {}. Skipping match.'.format(obj['docket'], obj['term']))
            continue

        # Roughly 80 seconds for 20 queries. - 4s per query.
        nPage = 1
        nLaterAppearance = 0
        previouslyUsed = False
        LN_query('"' + obj['match'] + '"', driver)
        while True:
            res = driver.find_elements_by_xpath('//*[@class="wrapper"]/ol/li')
            logging.info("Found {0} results on current page".format(str(len(res))))

            for item in res:
                try:
                    name_tag = item.find_element_by_class_name('doc-title')
                    name = name_tag.text
                    metadata_tag = item.find_element_by_tag_name('aside')
                    metadata = metadata_tag.text
                    fields = metadata.split('\n')
                except:
                    logging.error('Parsing some page element failed. Continuing')
                    continue

                date = 'unknown'
                foundDate = False
                for f in fields:
                    if foundDate:
                        date = f
                        break
                    if f.lower() == 'date':
                        foundDate = True

                datetime = time.strptime(date, '%b %d, %Y')
                if datetime < match_case['decided_date']:
                    previouslyUsed = True
                    print "found previous usage: "
                    print match_case['decided_date']
                    break
                elif datetime > match_case['decided_date']: # note the strict greater than. This will hopefully weed out the opinion itself
                    nLaterAppearance += 1

            paginators = driver.find_elements_by_xpath('//*[@class="pagination"]/ol/li')
            if len(paginators) == 0 or 'disabled' in paginators[-1].get_attribute('class'):
                logging.info("Reached end of results pages")
                break
            elif previouslyUsed:
                logging.info("Found previous usage, skipping to next match")
                break
            else:
                logging.info("Going to next results page")
                nPage += 1
                paginators[-1].click()
                waitUntilDriverLoaded(driver, "next page didn't load.", nPage, timeout=60)
        # end while{'term': term, 'docket': docket, 'brief': brief, 'match': match}
        line = '\t'.join([obj['term'], obj['docket'], obj['brief'], obj['match'], '1\tNA' if previouslyUsed else '0\t'+str(nLaterAppearance)]) + '\n'
        with open(file_in + '_laterAppearance.tsv', 'a') as f_new: #note: "append" mode.
            f_new.write(line)


    driver.quit()

