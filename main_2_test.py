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

# #####################
run_count = 0
# max_run_count = 6

second_between_dump = 10    #time period to store our real simulation data. each 60 seconds, store results
# second_between_dump = 10    #time period to store our real simulation data. each 60 seconds, store results
last_dump_time = 0
snapshot_num = 0

# #####################






# #####################
mika_go_PATH = './mika_go'

if len(sys.argv) < 2:
    print 'please input one arg ==> the main number'
    assert 0

if len(sys.argv) == 2:
    main_count = sys.argv[1]  # computer number identity
elif len(sys.argv) == 3:
    main_count = sys.argv[1]  # computer number identity
    second_between_dump = int(sys.argv[2])
else:
    print 'please input 1 or 2 argument.   1)computer number 2)record period'
    assert(0)    




### build input_dict. May change to "itertools.product" in the later version
input_dict = dict()    ### very import!!!  key to reset whole simulation
result_dic_list = list()
### end


while ( path.exists(mika_go_PATH) == True or run_count == 0):
    # if run_count >= max_run_count:
        # break


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
        # 4,
        # 5,
        # 8,
        16,
        # 64,
        # 128,
    ]

    # input_dict['src_num'] = 1
    # input_dict['src_num'] = 4
    # input_dict['src_num'] = 8
    # input_dict['src_num'] = 12
    src_num__LIST = [
        # 1,
        2,
        4,
        # 8,
        # 10,
        # 12,
        # 24,
        # 48,
    ]

    # input_dict['VMmigr_gen_type'] = 'srcFirst'  #'vmFirst' or 'srcFirst'.
    # input_dict['VMmigr_gen_type'] = 'vmFirst'  #'vmFirst' or 'srcFirst'.
    VMmigr_gen_type__LIST = [
        'vmFirst',
        'srcFirst',
    ]


    for tmpI2 in itertools.product(migr_type__LIST, tot_host_num__LIST, src_num__LIST, VMmigr_gen_type__LIST):

        # # #  iterate all types of topology snapshot
        input_dict['migr_type'] = tmpI2[0]
        input_dict['tot_host_num'] = tmpI2[1]
        input_dict['src_num'] = tmpI2[2]
        input_dict['VMmigr_gen_type'] = tmpI2[3]
        
        # # # skip some un-reasonable setting
        # if input_dict["src_num"] >= (input_dict["tot_host_num"]/float(2)):
            # continue                    

        # # # for use in snapshot_gen.py
        if input_dict['migr_type'] == 'Consolidation':
            src_tmp = (20, 35)
            input_dict [" src_upBWC_range "] = src_tmp
            input_dict [" src_dnBWC_range "] = src_tmp
            input_dict [" src_sigmaC_range "] = src_tmp
            dst_tmp = (70, 80)
            input_dict [" dst_upBWC_range "] = dst_tmp
            input_dict [" dst_dnBWC_range "] = dst_tmp
            input_dict [" dst_sigmaC_range "] = dst_tmp
        elif input_dict['migr_type'] == 'LoadBalancing':
            input_dict [" src_upBWC_range "] = (75, 95)
            input_dict [" src_dnBWC_range "] = (75, 95)
            input_dict [" src_sigmaC_range "] = (75, 95)
            input_dict [" dst_upBWC_range "] = (30, 50)
            input_dict [" dst_dnBWC_range "] = (30, 50)
            input_dict [" dst_sigmaC_range "] = (30, 50)
            
        # ###for use in snapshot_gen.py  parameters about VM
        vm_tmp = (5, 10)
        input_dict [" vm_upSBW_range "] = vm_tmp
        input_dict [" vm_dnSBW_range "] = vm_tmp
        input_dict [" vm_sigma_range "] = vm_tmp
        input_dict [" vm_ori_size_range "] = (30, 80)
        
        ### end




        ### generate snapshot
        # tmp_snapshot_file = './snapshot_archive/%s_%d.tmp' % (main_count, run_count)
        tmp_snapshot_file = './snapshot_archive/%s.tmp' % (main_count)
        # tmp_snapshot_file = 'tmp_snapshot_file.tmp'
        # keep_gen_snapshot = True
        keep_gen_snapshot = True
        if keep_gen_snapshot == True:
            gen_result = main_gen_snapshot(input_dict, tmp_snapshot_file)
            if gen_result == False:
                print 'main_2.py Sorry...no snapshot generated...skip to next setting'
                assert(0)
                continue

        

        ### different algo setting
        migration_mode__LIST = [
            'PreCopy', 
            'StopNCopy',
        ]
        algo_version__LIST = [
            'StrictSequence', 
            # 'RanSequence',
            # 'ConCurrent', 
        ]


        for tmpI in itertools.product(migration_mode__LIST, algo_version__LIST):
            input_dict['migration_mode'] = tmpI[0]
            input_dict['algo_version'] = tmpI[1]        
            print '\n\n==========>> new iteration'
            print 'this iteration gogo1: The input_dict is ==>' , input_dict['migration_mode'], input_dict['algo_version']
            dump_snapshot(tmp_snapshot_file)
            result_dict = main_G_run(input_dict, tmp_snapshot_file)
            input_dict_tmp = result_dict['input']
            result_dict['input'] = input_dict
            output_dict_tmp = result_dict['output']
            result_dic_list.append(str(result_dict))
            
            assert(str(input_dict) == str(input_dict_tmp)), 'main_2.py input different'
            print 'result_dic_list append element result_dict', result_dict
        ### end



        ### record the result to file
        if time.time() - last_dump_time > second_between_dump:
            last_dump_time = time.time()
            result_dic_file_name = './result_archive/%s_%d.result_dic' % (main_count, run_count)
            pickle.dump( result_dic_list, open( result_dic_file_name, "wb" ) )
            result_dic_list = list()

        run_count += 1
