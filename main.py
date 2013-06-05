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


os.system('cls') # on linux / os x




### build input_dict. May change to "itertools.product" in the later version
input_dict = dict()    ### very import!!!  key to reset whole simulation

###different topology generating via snapshot_gen.py
# # # vm snapshot generate by Consolidation or LoadBalancing  --> for louis related code. --> snapshot_gen.py
input_dict['migr_type'] = 'Consolidation'
# input_dict['migr_type'] = 'LoadBalancing'

input_dict['tot_host_num'] = 16
# input_dict['tot_host_num'] = 64

# input_dict['src_num'] = 1
input_dict['src_num'] = 4
# input_dict['src_num'] = 8
# input_dict['src_num'] = 12

# input_dict['VMmigr_gen_type'] = 'srcFirst'  #'vmFirst' or 'srcFirst'.
input_dict['VMmigr_gen_type'] = 'vmFirst'  #'vmFirst' or 'srcFirst'.


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


# ### different algo running  ==> for backup usage 
# ==> obsolete ==> move to later lines
# # # #vm migration mode  --> for mika related code --> basic.py
# # input_dict['migration_mode'] = 'StopNCopy'
# input_dict['migration_mode'] = 'PreCopy'

# input_dict['algo_version'] = 'StrictSequence'
# # input_dict['algo_version'] = 'ConCurrent'
# # input_dict['algo_version'] = 'RanSequence'
# ### end







### generate snapshot
# # generate VM and hosts, if at least one VM have not DST --> re-run snapshot_gen_func again
# keep_gen_snapshot = True
# keep_gen_snapshot = False

# result = False
# while keep_gen_snapshot:
    # G = Global_cl(input_dict)     #global data structure
    # result, vm__dict, host__dict = snapshot_gen(G, input_dict)

    # if result == True:
        # print 'main.py: snapshot_gen True \t', result
        # print 'vm_size:', len(vm__dict), 'host_size', len(host__dict)
        # G.all_VM__dict = vm__dict
        # G.all_host__dict = host__dict
        
        # print 'before pickle G=\n'        
        # pickle.dump( G, open( tmp_snapshot_file, "wb" ) ) 

        # keep_gen_snapshot = False
        # break
    # elif result == False:
        # print 'main.py: snapshot_gen False\t', result
    # else:
        # assert(0)
        
# assert(result == True or keep_gen_snapshot == False)
### end
main_gen_snapshot(input_dict, tmp_snapshot_file)



### different algo setting
# # #vm migration mode  --> for mika related code --> basic.py
# input_dict['migration_mode'] = 'StopNCopy'
# input_dict['migration_mode'] = 'PreCopy'

# input_dict['algo_version'] = 'StrictSequence'
# input_dict['algo_version'] = 'ConCurrent'
# input_dict['algo_version'] = 'RanSequence

migration_mode__LIST = ['PreCopy', 'StopNCopy']
# algo_version__LIST = ['StrictSequence', 'ConCurrent', 'RanSequence']
algo_version__LIST = ['StrictSequence', 'ConCurrent']
for tmpI in itertools.product(migration_mode__LIST, algo_version__LIST):
    input_dict['migration_mode'] = tmpI[0]
    input_dict['algo_version'] = tmpI[1]
    
    result_dict = main_G_run(input_dict, tmp_snapshot_file)
    input_dict_tmp = result_dict['input']
    output_dict_tmp = result_dict['output']
    # print 'this iteration success:  gogo. The input_dict is ==>', input_dict
    print 'this iteration success:  gogo. The input_dict is ==>' , input_dict['migration_mode'], input_dict['algo_version']
### end




######## Algorithm running: start
# G = None
# G = Global_cl(input_dict)     #global data structure
# # # use pickle to store and load G obj
# G_tmp = pickle.load( open( tmp_snapshot_file, "rb" ) )
# G.refresh_G(input_dict, G_tmp.all_host__dict, G_tmp.all_VM__dict)
# print 'after pickle G=\n', G
# print '\n\n'


# # initialization of vmm transmission
# print '---------->> now time:', 0, 'main.py before all vm schedule initialization'
# if input_dict['algo_version'] == 'StrictSequence':
    # func_SS_INIT(G)
# elif input_dict['algo_version'] == 'ConCurrent':
    # func_Concurrent(G, initFlag = True)
# else:
    # assert(0)


    
# # print '\n\n'
# E = G.E                 # event list
# print 'main.py: after initialization, some event are scheduled, event_list length =\t', len(E.list)
# assert(len(E.list) > 0)
# # continuous event based...vmm transmission
# while (len(E.list) > 0):
    # result, event_obj = E.upcoming_event()
    # if result == True:
        # G.now = event_obj.time
        # print '\n\n---------->> now time:', G.now, 'main.py --> activate one valid event. '
        
        # vm_num = event_obj.vm_num
        # G.all_VM__dict[vm_num].migration_over()

    # else:
        # print '---------->> main.py --> skip one obsolete event, event_num', event_obj.event_num

# ### add assert to ensure all vm_obj.status == 'completed'
# print 'all events have finished, computing results for the snapshot'
# output_dict = result_one_snap(G)

# result_dict = dict()
# result_dict['input'] = input_dict
# result_dict['output'] = output_dict
######## Algorithm running: end
