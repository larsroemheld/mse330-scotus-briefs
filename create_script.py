
import os
import subprocess
import pprint as pp
import re
import logging

# Parameters
op_dirname = "opinions"
briefs_dirname = "textified"
opinion_paths = os.listdir(os.path.abspath(op_dirname))
brief_paths = os.listdir(os.path.abspath(briefs_dirname))
report_folder = r'Z:\Desktop\reports'
opinion_base_path = r'Z:\Desktop\opinions'
brief_base_path = r'Z:\Desktop\textified'

# Regexes
opinion_re = re.compile(r'([\w\s\-\_]+)_opinion.txt')
brief_re   = re.compile(r'([\w\s\-\_]+)_amicus')

# Global Counters
total_num_files = 0

class Case:
    '''A structure to hold relevant paths for each case'''
    def __init__(self, identifier, op_num, brief_num):
        self.identifier = identifier
        self.opinion_path = ""
        self.brief_paths = []
        self.op_num = op_num
        self.brief_num = brief_num

    def add_opinion(self, filename):
        self.opinion_path = filename

    def add_brief(self, filename):
        self.brief_paths.append(filename)

counter = 1 # Copyfind document number starts from 1
caseid_case = {} # OT 2007_06-1037: Case object
for op_path in opinion_paths:
    match = opinion_re.search(op_path)
    if match is not None:
        case_identifier = match.group(1)
        caseid_case[case_identifier] = Case(case_identifier, counter, counter+1)
        caseid_case[case_identifier].add_opinion(op_path)
        total_num_files += 1
        counter += 2

for brief_path in brief_paths:
    match = brief_re.search(brief_path)
    if match is None:
        continue

    identifier = match.group(1)
    if identifier not in caseid_case:
        print "{} not found!".format(identifier)
        continue

    case = caseid_case[identifier] 
    case.add_brief(brief_path)
    total_num_files += 1

#### BEGIN CREATING SCRIPT #####
with open("script.txt", "w") as f:
    f.write("Documents,{}\n".format(total_num_files))
    f.write("ReportFolder,{}\n".format(report_folder))

    for key, case in caseid_case.iteritems():
        op_path = '\\'.join([opinion_base_path, case.opinion_path])
        f.write("Document,{},{}\n".format(case.op_num, op_path))

        for brief_file in case.brief_paths:
            full_brief_path = '\\'.join([brief_base_path, brief_file])
            f.write("Document,{},{}\n".format(case.brief_num, full_brief_path))
        
os.system("cat script_parts/configurations.txt >> script.txt")
with open("script.txt", "a") as f:
    for key, case in caseid_case.iteritems():
        f.write("Compare,{},{}\n".format(case.op_num, case.brief_num))
    f.write("Done")





