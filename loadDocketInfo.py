'''
Gets docket data from SCOTUSblog

Lars Roemheld, roemheld@stanford.edu
'''
__author__ = 'Lars Roemheld'

from bs4 import BeautifulSoup
import requests
import logging
import random
import os, sys, getopt
import json
import re
import urlparse


def loadCases(filename):
    '''
    Loads case dockets that were stored in a json file (such as the one created by downloadDockets.py
    :param filename:
    :return:
    '''
    with open(filename) as f:
        cases = json.load(f)
    return cases

def getCaseDocFilename(case, iDocument):
    '''
    Get the filename of the text file (txt) of a case document
    :param case: a case object
    :param iDocument: index of the document in that case (0-indexed)
    :return:
    '''
    term = case['Term']
    docketNo = case['Docket No.']
    documents = case.get('documents')
    if iDocument > (len(documents) - 1): return ""
    filename = documents[iDocument]['local_filename']
    return term + '_' + docketNo + '_' + filename[0:-4] + '.txt'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    cases = loadCases('cases.json')
    print 'Loaded {0} cases.'.format(str(len(cases)))

    iCase = 401
    iDoc = 1
    folder = 'textified/'
    print 'Docket from case {0} ({1}, {2} - {3})'.format(iCase, cases[iCase]['Docket No.'], cases[iCase]['Term'], cases[iCase].get('name'))
    print json.dumps(cases[iCase], indent=4, sort_keys=True)
    print '\n'
    print 'Showing document {0} from that case (type is {1}):'.format(iDoc, cases[iCase]['documents'][iDoc]['appeared_section'])
    temp = getCaseDocFilename(cases[iCase], iDoc)
    print 'Filename: ', temp
    with open(folder + temp, 'r') as f:
        content = f.read()
    print 'Size: ' + str(len(content)) + 'bytes'
    print 'First 200 Chars:\n'
    print content[0:200]
