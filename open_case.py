
# Note: brew install chromedriver (or pass the chromedriver executable path in the webdriver argument)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import sys
import re
from time import sleep


if __name__ == '__main__':
    assert(len(sys.argv) == 4)
    match = re.match(r'(\d{4})(.+)amicus', sys.argv[2])
    if not match:
        print "FORMAT NOT EXPECTED"
        exit(0);

    year = match.group(1)
    docket = match.group(2)
    
    match = re.match(r'briefs(\d+)', sys.argv[3])
    if not match:
        print "FORMAT NOT EXPECTED"
        exit(0);

    ab_num = match.group(1)

    reports_folder = "/Users/allenhuang/Desktop/phrase10/reports"
    filename = "file://" + reports_folder + "/OT%20" + year + "_" + docket + "_opinion.txt.OT%20" + year + "_" + docket + "_amicus%20briefs" + ab_num + ".txt.html"

    driver = webdriver.Chrome()
    driver.get(filename)


