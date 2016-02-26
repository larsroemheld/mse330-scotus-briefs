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
import os, logging

def waitUntilDriverLoaded(driver, error, timeout=120):
    # borrowed & adapted from https://github.com/stanford-bitcoin/bitcoin-twitter/blob/master/flask_selenium.py
    try:
        done = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body[status="done"]'))
        )
    except:
        print(error)
        exit()

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
    searchBar = driver.find_element_by_id('searchTerms')
    searchBar.clear()
    searchBar.send_keys(query + Keys.RETURN)
    resultsList = driver.find_elements_by_xpath('//*[@class="wrapper"]/ol/li')
    logging.info("Found {0} 1st-page results for query {1}".format(str(len(resultsList)), query))
    paginators = driver.find_elements_by_xpath('//*[@class="pagination"]/ol/li')
    if len(paginators) > 0:
        logging.info("Total number of pages: {0}".format(paginators[-2].text))
    else:
        logging.info("No additional pages found")

    return resultsList


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    driver = webdriver.Chrome()

    # Note
    # export LEXISNEXIS_USER=username
    # export LEXISNEXIS_PASS=password
    LN_user = os.environ.get('LEXISNEXIS_USER')
    LN_pass = os.environ.get('LEXISNEXIS_PASS')
    if LN_pass is None or LN_pass is None:
        logging.error('Could not find LexisNexis credentials in environ variables. Aborting.')
        exit()

    if not LN_login(LN_user, LN_pass, driver):
        exit()

    # ugly, but works :D
    logging.warning('Please change the search scope to "cases" only -- you have 20 seconds.')
    time.sleep(10)
    logging.warning('Please change the search scope to "cases" only -- you have 10 seconds.')
    time.sleep(10)

    # Roughly 80 seconds for 20 queries. - 4s per query.
    res = LN_query('lars roemheld', driver)
    for item in res:
        name_tag = item.find_element_by_class_name('doc-title')
        name = name_tag.text
        metadata_tag = item.find_element_by_tag_name('aside')
        metadata = metadata_tag.text
        fields = metadata.split('\n')

        date = 'unknown'
        foundDate = False
        for f in fields:
            if foundDate:
                date = f
                break
            if f.lower() == 'date':
                foundDate = True

        print name + " : " + date

    driver.quit()

