import pickle
import glob
import copy

from os import path
from init_parameter import ALL_RESULT_LIST, ALL_SETTING_LIST

name_filter = '*.result_dic'
target_path = 'result_archive'
write_path = 'aggr_result/'

iter_result = {}
for infile in glob.glob( path.join(target_path, name_filter) ):
    try:
        result_dic_list = pickle.load( open( infile, "rb" ) )
    except EOFError:
        continue

    for item in result_dic_list:
        tmp_result_dic = eval(item)
        # tmp_result_dic = result_dic_list[i]        
        
    # for i in range(len(result_dic_list)):
        # tmp_result_dic = result_dic_list[i]
        key = tmp_result_dic['input']
        print 'aggregate_result_dic.py  key', key['migration_mode'] , key['algo_version']
        key = str(tmp_result_dic['input'])
        value = tmp_result_dic['output']
        
        if iter_result.has_key(key) == False:
            iter_result[key] = dict()
            iter_result[key]['list'] = list()
            iter_result[key]['avg_result'] = dict()
        iter_result[key]['list'].append(value)
        # print 'build iter_result key',  key
        print 'build iter_result value',  value
        
        
for key in iter_result:
    result__list = iter_result[key]['list']
    assert len(result__list) > 0
    
    iter_num = len(result__list)
    
    # # # list_item contain many results in the same settings
    tmp_dict = dict()
    tmp_avg_dict = dict()
    for var_checking in ALL_RESULT_LIST:
        tmp_dict[var_checking] = list()    
        
    for list_item in result__list:
        for var_checking in ALL_RESULT_LIST:
            tmp_dict[var_checking] .append(list_item[var_checking])
    for var_checking in ALL_RESULT_LIST:
        iter_result[key]['avg_result'][var_checking] = sum(tmp_dict[var_checking]) / float(len(tmp_dict[var_checking]))
            
    iter_result[key]['avg_result']['iter_num'] = iter_num
    
ALL_RESULT_LIST.append('iter_num')

    
    
# print "iter_result", iter_result

##################################
# print the first line to explain the column name
# column name I want~~~
out_file_detail_line = ''

# col_set_want_list = ['total_vm_num', "node_type", "initial_BW", "initial_size"]
col_set_want_list = ALL_SETTING_LIST
for i in range(len(col_set_want_list)):
    col_name = col_set_want_list[i]
    out_file_detail_line += col_name + '\t'
    
# col_result_want_list = ['iter_num', 'avg_noMatchProb', 'avg_differencePercent', 'avg_ranDifferencePercent']
col_result_want_list = ALL_RESULT_LIST
for i in range(len(col_result_want_list)):
    col_name = col_result_want_list[i]
    out_file_detail_line += col_name + '\t'    

out_file_detail_line += '\n'


##################################
# print the following line to display the column value

for key in iter_result:
    result_dic = iter_result[key]['avg_result']
    key_dict = eval(key)
    
    for i in range(len(col_set_want_list)):
        col_name = col_set_want_list[i]
        j = str(key_dict[col_name])
        out_file_detail_line += j + '\t'
        
    for i in range(len(col_result_want_list)):
        col_name = col_result_want_list[i]
        j = str(result_dic[col_name])
        out_file_detail_line += j + '\t'
    
    out_file_detail_line += '\n'
    
        
FILE_config_w = open(write_path + 'filter_out.result', "w")
FILE_config_w.write(out_file_detail_line)
FILE_config_w.close()