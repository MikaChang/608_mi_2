# -*- coding: utf-8 -*-�@
from __future__ import division
import math

# from decimal import *
# getcontext().prec = 6


# # for StrictSequence algo
# # import init_update_func as init_func
# # import function as func
# from init_update_func import init_func
# import function as func

# # for ConCurrent
# import concurrent_case as ConCur_py

# # for result_one_snapshot
# import result_one_snapshot as result_one_snapshot_py



# # for snapshot generation
# import snapshot_gen as snapshot_gen_func
# from snapshot_gen import *

####
# temp pickle file to store the snapshot
tmp_snapshot_file = 'tmp_snapshot_file.tmp'

SET__set = set([1,2,3])  # set 1,2,3
GP__set = set([1,2,3])   # group 1,2,3

# # # time precision
SLOTTIME = 1e-6

# # # rate precision
RATE_PRECISION = 1e-6

# # #
# ACCEPTABLE_MINI_VMM_DATA_RATE = 0.1
ACCEPTABLE_MINI_VMM_DATA_RATE = 1e-6



MAX_COUNT_for_snapshot_gen_fail = 10


### # # for aggregate_result_dic.py
ALL_SETTING_LIST = [
    'tot_host_num',
    'src_num',
    'migr_type',    
    'VMmigr_gen_type',    
    'vm_sel_mode',
    'migration_mode',
    'algo_version',
    'SS_level',
]

ALL_RESULT_LIST = [
    'total_vm_num',
    'accu_vm_migration_period',
    'sys_migration_period',    
    'accu_vm_deployment_time',
]

