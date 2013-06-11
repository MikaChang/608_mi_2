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

# #####################


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


    
    
    
    
    
# #####################
keep_gen_snapshot = True
# keep_gen_snapshot = False

FILTER_ERROR_ITERATION_by_subprocess = True
# FILTER_ERROR_ITERATION_by_subprocess = False


# tmp_snapshot_file = './snapshot_archive/%s_%d.tmp' % (main_count, run_count)
tmp_snapshot_file = './snapshot_archive/snapshot_%s.tmp' % (main_count)
# tmp_snapshot_file = 'tmp_snapshot_file.tmp'
tmp_result_dict_file = './snapshot_archive/result_dict_%s.tmp' % (main_count)

# #####################
run_count = 0
# max_run_count = 6
second_between_dump = 10    #time period to store our real simulation data. each 60 seconds, store results
# second_between_dump = 10    #time period to store our real simulation data. each 60 seconds, store results
last_dump_time = 0

mika_go_PATH = './mika_go'
# #####################



### build input_dict. May change to "itertools.product" in the later version
input_dict = dict()    ### very import!!!  key to reset whole simulation
result_dic_list = list()

# # # some hand made input_dict, still not merge to the automation iteration generation code in the following


# # #  the following input_dict are merged into iteration generation code
###different topology generating via snapshot_gen.py
# # # vm snapshot generate by Consolidation or LoadBalancing  --> for louis related code. --> snapshot_gen.py
# input_dict['migr_type'] = 'Consolidation'
# input_dict['migr_type'] = 'LoadBalancing'
migr_type__LIST = [
    'Consolidation',
    'LoadBalancing',
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
    6,
    # 8,
    # 10,
    # 12,
    # 24,
    # 36,
    # 48,
    # 50,
    # 60,
    
]

# input_dict['VMmigr_gen_type'] = 'srcFirst'  #'vmFirst' or 'srcFirst'.
# input_dict['VMmigr_gen_type'] = 'vmFirst'  #'vmFirst' or 'srcFirst'.
# for Consolidation Case
VMmigr_gen_type__LIST = [
    # 'vmFirst',
    'srcFirst',
]


# VM selection policy for LoadBalancing Case
vm_sel_mode__LIST = [
    'random',
    'ascending',
    'descending'
]    
###different topology generating via snapshot_gen.py end



### different algo setting
migration_mode__LIST = [
    'PreCopy', 
    'StopNCopy',
]
algo_version__LIST = [
    'StrictSequence', 
    'RanSequence',
    'ConCurrent', 
]


# # # SS SubControl. full=> wait for the access link full BW,  partial=> use the timely residual BW.
# # # SS only  'full' , or 'partial' ==> used in basic.py speed_checking()
SS_level__LIST = [
    'full',
    'partial'
]
### end





while ( path.exists(mika_go_PATH) == True or run_count == 0):
    # if run_count >= max_run_count:
        # break

    for tmpI2 in itertools.product(migr_type__LIST, tot_host_num__LIST, src_num__LIST, VMmigr_gen_type__LIST, vm_sel_mode__LIST):

        # # #  iterate all types of topology snapshot
        input_dict['migr_type'] = tmpI2[0]
        input_dict['tot_host_num'] = tmpI2[1]
        input_dict['src_num'] = tmpI2[2]
        input_dict['VMmigr_gen_type'] = tmpI2[3]
        input_dict['vm_sel_mode'] = tmpI2[4]
        
        # # # skip some un-reasonable setting
        if input_dict["src_num"] >= (input_dict["tot_host_num"]/float(2)):
            continue
            
        # # # exclude some redundant setting
        if input_dict['migr_type'] != 'LoadBalancing' and input_dict['vm_sel_mode'] != 'random':
            continue

            

        # # # for use in snapshot_gen.py
        if input_dict['migr_type'] == 'Consolidation':
            src_tmp = (20, 30)
            input_dict [" src_upBWC_range "] = src_tmp
            input_dict [" src_dnBWC_range "] = src_tmp
            input_dict [" src_sigmaC_range "] = src_tmp
            dst_tmp = (70, 80)
            input_dict [" dst_upBWC_range "] = dst_tmp
            input_dict [" dst_dnBWC_range "] = dst_tmp
            input_dict [" dst_sigmaC_range "] = dst_tmp
        elif input_dict['migr_type'] == 'LoadBalancing':
            src_tmp = (80, 90)  
            input_dict [" src_upBWC_range "] = src_tmp
            input_dict [" src_dnBWC_range "] = src_tmp
            input_dict [" src_sigmaC_range "] = src_tmp
            dst_tmp = (30, 40)
            input_dict [" dst_upBWC_range "] = dst_tmp
            input_dict [" dst_dnBWC_range "] = dst_tmp
            input_dict [" dst_sigmaC_range "] = dst_tmp
            
        # ###for use in snapshot_gen.py  parameters about VM
        vm_tmp = (1, 4)
        input_dict [" vm_upSBW_range "] = vm_tmp
        input_dict [" vm_dnSBW_range "] = vm_tmp
        input_dict [" vm_sigma_range "] = vm_tmp
        input_dict [" vm_ori_size_range "] = (30, 80)


        ### generate snapshot
        if keep_gen_snapshot == True:
            if FILTER_ERROR_ITERATION_by_subprocess == False :
                gen_result = main_gen_snapshot(input_dict, tmp_snapshot_file)
                if gen_result == False:      # # # False comes from main_gen_snapshot     1 comes from subprocess
                    print 'main_2.py Sorry...no snapshot generated...skip to next setting'
                    # assert(0)
                    continue                
                    
            elif FILTER_ERROR_ITERATION_by_subprocess == True:
                gen_result =subprocess.call(['python', 'main_gen_snapshot_run2file.py', str(input_dict), str(tmp_snapshot_file)])
                # # # gen_result = 1 ==> subprocess FAIL
                if gen_result == 1:      # # # False comes from main_gen_snapshot     1 comes from subprocess
                    print 'main_2.py Sorry...no snapshot generated...skip to next setting'
                    # assert(0)
                    continue

                
                
        ### run iteration: start
        snapshot_result_dic_list = list()
        this_snapshot_all_algo_success = True
        for tmpI in itertools.product(migration_mode__LIST, algo_version__LIST, SS_level__LIST):
            input_dict['migration_mode'] = tmpI[0]
            input_dict['algo_version'] = tmpI[1]
            input_dict['SS_level'] = tmpI[2]
            
            # # # exclude some redundant setting
            if input_dict['algo_version'] == 'StrictSequence' and input_dict['SS_level'] != 'full':
                continue
            elif input_dict['algo_version'] == 'RanSequence' and input_dict['SS_level'] != 'partial':
                continue
            
            
            
            print '\n\n==========>> new iteration'
            print 'this iteration gogo1: The input_dict is ==>' , input_dict['migration_mode'], input_dict['algo_version']
            dump_snapshot(tmp_snapshot_file)
            
            if FILTER_ERROR_ITERATION_by_subprocess == False:
                result_dict = main_G_run(copy.deepcopy(input_dict), tmp_snapshot_file)
            elif FILTER_ERROR_ITERATION_by_subprocess == True:
                None
                sub_pro_result =subprocess.call(['python', 'main_G_run2file.py', str(input_dict), str(tmp_snapshot_file), str(tmp_result_dict_file)])
                if sub_pro_result == 0:       # # #  0==> subprocess SUCCESS
                    result_dict = pickle.load( open( tmp_result_dict_file, "rb" ) )
                else:
                    sys.stderr, 'This iteration FAIL'
                    this_snapshot_all_algo_success = False
                    snapshot_result_dic_list = list()
                    break
            else:
                assert(0)
            snapshot_result_dic_list.append(str(result_dict))
            print 'result_dic_list append element result_dict', result_dict
        ### run iteration: end
        if this_snapshot_all_algo_success == True:
            for re in snapshot_result_dic_list:
                result_dic_list.append(re)


        ### record the result to file
        if time.time() - last_dump_time > second_between_dump:
            last_dump_time = time.time()
            result_dic_file_name = './result_archive/%s_%d.result_dic' % (main_count, run_count)
            pickle.dump( result_dic_list, open( result_dic_file_name, "wb" ) )
            result_dic_list = list()

        run_count += 1
