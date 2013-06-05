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
from os import path

os.system('cls') # on linux / os x
# ######################
run_count = 0
# max_run_count = 1
# ######################


# #####################
mika_go_PATH = './mika_go'

if len(sys.argv) < 2:
    print 'please input one arg ==> the main number'
    assert 0

second_between_dump = 60    #time period to store our real simulation data. each 60 seconds, store results
second_between_dump = 1    #time period to store our real simulation data. each 60 seconds, store results
last_dump_time = 0

if len(sys.argv) == 2:
    main_count = sys.argv[1]  # computer number identity
elif len(sys.argv) == 3:
    main_count = sys.argv[1]  # computer number identity
    second_between_dump = int(sys.argv[2])
else:
    print 'please input 1 or 2 argument.   1)computer number 2)record period'
    assert(0)    
# #####################


### build input_dict. May change to "itertools.product" in the later version
input_dict = dict()    ### very import!!!  key to reset whole simulation

result_dic_list = []
### end


###different topology generating via snapshot_gen.py
# # # vm snapshot generate by Consolidation or LoadBalancing  --> for louis related code. --> snapshot_gen.py
# input_dict['migr_type'] = 'Consolidation'
# input_dict['migr_type'] = 'LoadBalancing'
migr_type__LIST = [
    'Consolidation',
    # 'LoadBalancing',
]

# input_dict['tot_host_num'] = 16
# input_dict['tot_host_num'] = 64
tot_host_num__LIST = [
    16,
    # 64,
]

# input_dict['src_num'] = 1
# input_dict['src_num'] = 4
# input_dict['src_num'] = 8
# input_dict['src_num'] = 12
src_num__LIST = [
    # 1,
    4,
    # 8,
    # 10,
    # 12,
]

# input_dict['VMmigr_gen_type'] = 'srcFirst'  #'vmFirst' or 'srcFirst'.
# input_dict['VMmigr_gen_type'] = 'vmFirst'  #'vmFirst' or 'srcFirst'.
VMmigr_gen_type__LIST = [
    'vmFirst',
    # 'srcFirst',
]


for tmpI2 in itertools.product(migr_type__LIST, tot_host_num__LIST, src_num__LIST, VMmigr_gen_type__LIST):
    
    # # #  iterate all types of topology snapshot
    input_dict['migr_type'] = tmpI2[0]
    input_dict['tot_host_num'] = tmpI2[1]
    input_dict['src_num'] = tmpI2[2]
    input_dict['VMmigr_gen_type'] = tmpI2[3]

    if input_dict['migr_type'] == 'Consolidation':
        input_dict [" src_upBWC_range "] = (25, 30)
        input_dict [" src_dnBWC_range "] = (25, 30)
        input_dict [" src_sigmaC_range "] = (25, 30)
        input_dict [" dst_upBWC_range "] = (70, 75)
        input_dict [" dst_dnBWC_range "] = (70, 75)
        input_dict [" dst_sigmaC_range "] = (70, 75)
    elif input_dict['migr_type'] == 'LoadBalancing':
        input_dict [" src_upBWC_range "] = (75, 95)
        input_dict [" src_dnBWC_range "] = (75, 95)
        input_dict [" src_sigmaC_range "] = (75, 95)
        input_dict [" dst_upBWC_range "] = (30, 50)
        input_dict [" dst_dnBWC_range "] = (30, 50)
        input_dict [" dst_sigmaC_range "] = (30, 50)
    ### end




    ### generate snapshot
    main_gen_snapshot(input_dict, tmp_snapshot_file)



    ### different algo setting
    migration_mode__LIST = [
        'PreCopy', 
        'StopNCopy'
    ]
    algo_version__LIST = [
        'StrictSequence', 
        'ConCurrent', 
        # 'RanSequence',
    ]


    for tmpI in itertools.product(migration_mode__LIST, algo_version__LIST):
        input_dict['migration_mode'] = tmpI[0]
        input_dict['algo_version'] = tmpI[1]        
        print 'this iteration gogo: The input_dict is ==>' , input_dict['migration_mode'], input_dict['algo_version']
        
        result_dict = main_G_run(input_dict, tmp_snapshot_file)
        input_dict_tmp = result_dict['input']
        output_dict_tmp = result_dict['output']
        result_dic_list.append(result_dict)
    ### end



    ### record the result to file
    if time.time() - last_dump_time > second_between_dump:
        last_dump_time = time.time()
        result_dic_file_name = './result_archive/%s_%d.result_dic' % (main_count, run_count)
        pickle.dump( result_dic_list, open( result_dic_file_name, "wb" ) )
        result_dic_list = list()

    run_count += 1
