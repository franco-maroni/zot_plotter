'''
Created on Jan 24, 2017

@author: francesco
'''

import os
from datetime import datetime as dt
import re

class VerificationResult(object):
    '''
    classdocs
    '''

    def __init__(self,
                 result_file_path=None,
                 outcome=None,
                 verification_time=None,
                 timestamp=None,
                 timestamp_str=None):
        '''
        Constructor
        '''
        self.result_file_path = result_file_path
        self.outcome = outcome
        self.verification_time = verification_time
        self.timestamp = timestamp
        self.timestamp_str = timestamp_str


class VerificationTrace(object):
    '''
    classdocs
    '''

    def __init__(self,
                 output_trace_file_path=None,
                 time_bound=None, records=None,
                 bool_set=None):
        '''
        Constructor
        '''
        self.time_bound = time_bound
        self.records = records
        self.bool_set = bool_set





class ZotResult(VerificationResult):
    '''
    classdocs
    '''
# standard result file for zot (containing verification outcome)
    result_file = 'output.1.txt'
    # standard history file for zot (containing output trace)
    hist_file = 'output.hist.txt'
    timestamp_format = "%Y-%m-%d__%H-%M-%S"

    def __init__(self, result_dir):
        '''
        Constructor
        '''
        self.result_dir = os.path.abspath(result_dir)
        self.result_file_path = os.path.join(self.result_dir, self.result_file)
        with open(self.result_file_path) as res_f:
            lines = res_f.readlines()
        self.outcome = None
        self.all_stats = None
        self.verification_time = None
        self.max_memory = None
        self.memory = None
        self.timestamp = None
        self.timestamp_str = None
        if lines:
            self.outcome = lines[0].strip()
            self.all_stats = {y[0]: y[1] for x in lines[-1:-32:-1] if ':' in x for y in
                              [re.sub(' +', ' ', x).strip().strip(':').strip(')').split(' ')]}
            self.verification_time = float(self.all_stats['time'])
            self.max_memory = float(self.all_stats['max-memory'])
            self.memory = float(self.all_stats['memory'])
            if self.outcome == 'sat':
                print 'Outcome is {} '.format(self.outcome.upper())
                # app_dir+'/'+'output.hist.txt'
                my_file_path = os.path.join(self.result_dir, self.hist_file)
                print 'I AM in {}'.format(os.getcwd())
                # GETTING LAST MODIFIED DATE FROM THE FILE
                moddate_seconds = os.stat(my_file_path)[8]  # 10 attributes
                self.timestamp = dt.fromtimestamp(moddate_seconds)
                self.timestamp_str = (self.timestamp
                                      .strftime(self.timestamp_format))
            elif self.outcome == 'unsat':
                print 'Outcome is {} '.format(self.outcome.upper())
            else:
                print ("Outcome: {} -> \n\n THERE MIGHT BE A PROBLEM. check {} for further info."
                       .format(self.outcome, self.result_file))
            print "Verification time: {}".format(self.verification_time)
            print "Max-memory: {} - Memory: {}".format(self.max_memory, self.memory)
            print "Result saved to {} directory".format(self.result_dir)


class ZotTrace(VerificationTrace):
    '''
    classdocs
    '''

    def __init__(self, output_trace_file_path):
        '''
        Constructor
        Parse history trace and save variable values in a dictionary.
        '''
        step = -1
        records = {}
        bool_set = set()
        f = open(output_trace_file_path)
        for line in f:
            line = line.strip()   # strip out carriage return
            if line.startswith("------ time"):
                step += 1
    #            print("------- STEP {0} -------".format(step))
            elif line.startswith("------ end"):
                pass
            elif line.strip() == "**LOOP**":
                records["LOOP"] = step
            else:
                key_value = line.split(" = ")  # split line into key and value
                key = key_value[0]   # key is first item in list
                if len(key_value) > 1:  # counter variable
                    value = key_value[1]   # value is 2nd item
                else:  # boolean variable (only key in trace)
                    value = step  # save list of step indexes for which boolean var is true
                    bool_set.add(key)
                # print key
                if key in records:
                    records[key].append(value)
                else:
                    records[key] = [value]
        self.bool_set = bool_set
        self.records = records
        self.time_bound = step
