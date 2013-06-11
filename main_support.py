# import basic
import init_parameter
from basic import *
from snapshot_gen import *
from init_update_func import *
from concurrent_case import *
from result_one_snapshot import *
from randomCase import *
import pickle, json
# import cPickle as pickle
import pickle
import os
import itertools
import pprint
import copy


def main_gen_snapshot(input_dict_tmp, tmp_snapshot_file):

    # generate VM and hosts, if at least one VM have not DST --> re-run snapshot_gen_func again
    keep_gen_snapshot = True
    # keep_gen_snapshot = False

    snapshot_gen_count_tmp = 0

    result = False
    while keep_gen_snapshot:
        input_dict = copy.deepcopy(input_dict_tmp)
        G = Global_cl(input_dict)     #global data structure
        result, vm__dict, host__dict = snapshot_gen(G, input_dict)
        print '\n\n\nmain_support.py snapshot_gen out  =result, len(vm), len(host)', result, len(vm__dict), len(host__dict)
        assert((vm__dict) >= 0 and len(host__dict) >= 0), (len(vm__dict), len(host__dict))
        
        if result == True:
            print 'main.py: snapshot_gen True \t', result
            print 'vm_size:', len(vm__dict), 'host_size', len(host__dict)
            G.all_VM__dict = vm__dict
            G.all_host__dict = host__dict
            
            print 'before pickle G=\n'        
            pickle.dump( G, open( tmp_snapshot_file, "wb" ) ) 

            keep_gen_snapshot = False
            break
        elif result == False:
            print 'main.py: snapshot_gen False\t', result
            print 'vm_size:', len(vm__dict), 'host_size', len(host__dict), 'src_num', input_dict['src_num']
            snapshot_gen_count_tmp += 1
            if snapshot_gen_count_tmp >= MAX_COUNT_for_snapshot_gen_fail:
                assert(0)
                return False
        else:
            assert(0)
            
    assert(result == True or keep_gen_snapshot == False)



def dump_snapshot(tmp_snapshot_file):
    G_tmp = pickle.load( open( tmp_snapshot_file, "rb" ) )
    all_host__dict = G_tmp.all_host__dict
    all_VM__dict = G_tmp.all_VM__dict
    
    print '\n\n\n\n\nprint out snapshot====> start'
    for key, obj in G_tmp.all_host__dict.items():
        obj.print_out()
    for key, obj in G_tmp.all_VM__dict.items():
        obj.print_out()
    print 'print out snapshot====> end'    

    
    


def main_G_run(input_dict, tmp_snapshot_file):
######## Algorithm running: start
    print 'main_support.main_G_run() gogo2: The input_dict is ==>' , input_dict['migration_mode'], input_dict['algo_version']
    G = None
    G = Global_cl(input_dict)     #global data structure
    # # use pickle to store and load G obj
    G_tmp = pickle.load( open( tmp_snapshot_file, "rb" ) )
    G.refresh_G(input_dict, G_tmp.all_host__dict, G_tmp.all_VM__dict)
    print 'after pickle G=\n', G
    print '\n\n'

    # initialization of vmm transmission
    print '---------->> now time:', 0, 'main.py before all vm schedule initialization'
    if input_dict['algo_version'] == 'StrictSequence':
        func_SS_INIT(G)
    elif input_dict['algo_version'] == 'ConCurrent':
        func_Concurrent_Init(G)
    elif input_dict['algo_version'] == 'RanSequence':
        func_ran_disjoint_init(G)
    else:
        assert(0)


        
    # print '\n\n'
    E = G.E                 # event list
    print 'main.py: after initialization, some event are scheduled, event_list length =\t', len(E.list)
    assert(len(E.list) > 0)
    # continuous event based...vmm transmission
    while (len(E.list) > 0):
        result, event_obj = E.upcoming_event()
        if result == True:
            G.now = event_obj.time
            print '\n\n---------->> now time:', G.now, 'main.py --> activate one valid event. '
            
            vm_num = event_obj.vm_num
            G.all_VM__dict[vm_num].migration_over()

        else:
            # print '---------->> main.py --> skip one obsolete event, event_num', event_obj.event_num
            None

    ### add assert to ensure all vm_obj.status == 'completed'
    print 'all events have finished, computing results for the snapshot'
    output_dict = result_one_snap(G)

    result_dict = dict()
    result_dict['input'] = input_dict
    result_dict['output'] = output_dict
    
    print 'main_support.main_G_run() gogo3: The input_dict is ==>' , result_dict['input']['migration_mode'], result_dict['input']['algo_version']
    
    return result_dict
    ######## Algorithm running: end

