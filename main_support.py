# import basic
import init_parameter
from basic import *
from snapshot_gen import *
from init_update_func import *
from concurrent_case import *
from result_one_snapshot import *
import pickle, json
# import cPickle as pickle
import pickle
import os
import itertools
import pprint



def main_gen_snapshot(input_dict, tmp_snapshot_file):
    # generate VM and hosts, if at least one VM have not DST --> re-run snapshot_gen_func again
    keep_gen_snapshot = True
    # keep_gen_snapshot = False

    result = False
    while keep_gen_snapshot:
        G = Global_cl(input_dict)     #global data structure
        result, vm__dict, host__dict = snapshot_gen(G, input_dict)

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
        else:
            assert(0)
            
    assert(result == True or keep_gen_snapshot == False)
    # return G




def main_G_run(input_dict, tmp_snapshot_file):
######## Algorithm running: start
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
        func_Concurrent(G, initFlag = True)
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
            print '---------->> main.py --> skip one obsolete event, event_num', event_obj.event_num

    ### add assert to ensure all vm_obj.status == 'completed'
    print 'all events have finished, computing results for the snapshot'
    output_dict = result_one_snap(G)

    result_dict = dict()
    result_dict['input'] = input_dict
    result_dict['output'] = output_dict
    
    return result_dict
    ######## Algorithm running: end
