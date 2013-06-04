import sys
import pickle

import mika_random
import itertools
import pickle

import time

from os import path


######################
run_count = 0
max_run_count = 1


total_vm_num_list = [2, 4, 6, 8]
node_type_list = ["DST", "SRC"]
initial_BW_list = [10, 20, 30, 40, 50, 60, 70, 80, 90]
initial_size_list = [10, 20, 30, 40, 50, 60, 70, 80, 90]

# total_vm_num_list = [4]
# node_type_list = ["SRC"]
# initial_BW_list = [10]
# initial_size_list = [40]
######################






# #####################
mika_go_PATH = './mika_go'

if len(sys.argv) < 2:
    print 'please input one arg ==> the main number'
    assert 0

second_between_dump = 60    #time period to store our real simulation data. each 60 seconds, store results

if len(sys.argv) == 2:
    main_count = sys.argv[1]  # computer number identity
elif len(sys.argv) == 3:
    main_count = sys.argv[1]  # computer number identity
    second_between_dump = int(sys.argv[2])
else:
    print 'please input 1 or 2 argument.   1)computer number 2)record period'
    assert(0)    
# #####################



result_dic_list = list()
last_dump_time = 0
while ( path.exists(mika_go_PATH) == True):
    # if run_count >= max_run_count:
        # break


        
    for r in itertools.product(total_vm_num_list, node_type_list, initial_BW_list, initial_size_list):
        # if path.exists(mika_go_PATH) != True:
            # break
          
        input_varible_dic = dict()
        input_varible_dic["total_vm_num"] = r[0]
        input_varible_dic["node_type"] = r[1]
        input_varible_dic["initial_BW"] = r[2]
        input_varible_dic["initial_size"] = r[3]
        
        if input_varible_dic["node_type"] == "DST" and input_varible_dic["initial_size"] > 50:
            continue            
        elif input_varible_dic["node_type"] == "DST" and input_varible_dic["initial_BW"] < 50:
            continue                                
        elif input_varible_dic["node_type"] == "SRC" and input_varible_dic["initial_size"] < 50:
            continue            
        elif input_varible_dic["node_type"] == "SRC" and input_varible_dic["initial_BW"] > 50:
            continue                                        
        

        input_varible_dic, output_dic = small_testing.sequence_testing(input_varible_dic)
        # print "input_varible_dic:", input_varible_dic, " output_dic", output_dic

        result_dic = dict()
        result_dic['input'] = input_varible_dic
        result_dic['output'] = output_dic
        
        result_dic_list.append(result_dic)

        # if len(result_dic_list) == 1000:
        if time.time() - last_dump_time > second_between_dump:
            last_dump_time = time.time()
            result_dic_file_name = './result_archive/%s_%d.result_dic' % (main_count, run_count)
            pickle.dump( result_dic_list, open( result_dic_file_name, "wb" ) )
            result_dic_list = list()

        run_count += 1
