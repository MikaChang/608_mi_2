# import basic
import init_parameter
from basic import *
from snapshot_gen import *
from init_update_func import *

from concurrent_case import *
from result_one_snapshot import *

from main_support import *

import pickle, json
# import cPickle as pickle
import pickle
import os
import itertools
import pprint
import time
import sys

import pdb
import subprocess


from os import path



### In the following code, I try to make main_support.py become exectable pyton code.
# # # main.py can use subprocess to call main_support.py. This isolate the assert error from the main.py
# # #the reuslt_dict is returned by the file
if len(sys.argv) != 3:
    # print 'please input 3 arg in string type==>\n 1)input_dict 2)snapshot_file, 3)result_dict_file'
    print 'please input 3 arg in string type==>\n 1)input_dict 2)snapshot_file'
    assert 0

# assert(0)

input_dict = eval(sys.argv[1])
tmp_snapshot_file = str(sys.argv[2])
# tmp_result_dict_file = str(sys.argv[3])

###
main_gen_snapshot(input_dict, tmp_snapshot_file)
###
