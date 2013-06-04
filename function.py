import basic
import random

def func_SS_G1(G):
    DST_num__set = G.DST_host__set & GPNum_to_host__dict[1]
    SRC_num__set = G.SRC_host__set & GPNum_to_host__dict[1]
        
    ### SRC host set
    for host_num in SRC_num__set:
        host_obj = G.all_host__dict[host_num]
        
        tuple__list = []   # store tuple (vm_obj, feasible_rate)
        for vm_num in host_obj.reg_q__Set:
            vm_obj = G.all_VM__dict[vm_num]
            result, miniRate = vm_obj.speed_checking('full', 'DST')
            if result == 'success':
                tuple__list.append( (vm_obj, miniRate) )
        
        seq_vm_obj__list = []
        seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1])   #from small to large
        
        # inv__list = seq_vm_obj__list[::-1]
        for vm_obj,  miniRate in seq_vm_obj__list:
            tmp_result, tmp_miniRate = vm_obj.speed_checking('full', 'DST')
            if tmp_result == 'success':
                vm_obj.assign_VM_BW(tmp_miniRate)
            

    
    ###  DST host set
    for host_num in DST_num__set:
        host_obj = G.all_host__dict[host_num]
        
        vm_obj__list = []
        for vm_num in host_obj.waiting_vm__set:
            vm_obj = G.all_VM__dict[vm_num]
            if vm_obj.dominant == 'DST':
                vm_obj__list.append(vm_obj)
        seq_vm_obj__list = sorted(vm_obj__list, key=lambda VM_cl2: VM_cl2.dnSBratio)
        
        ### only waiting for the first SRC        
        for vm_obj in seq_vm_obj__list:
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'DST')
            if result == 'success':
                vm_obj.assign_VM_BW(miniRate)
                break
            else:
                SRCnum = vm_obj.SRCnum
                G.all_host__dict[SRCnum].reg_q__Set.add(vm_obj.vm_num)
                break

def func_SS(G, GPNum, sort_mode):
    print 'function.py  func_SS()  GPNum', GPNum, 'sort_mode', sort_mode
    if GPNum == 1:
        unDomiSide_num='vm_obj.SRCnum'
        DomiSide='DST'
        unDomiSide_num__set = 'SRC_num__set'
        DomiSide_num__set = 'DST_num__set'
        DomiMetric='VM_cl2.dnSBratio'
    elif GPNum == 2 or GPNum == 3:
        unDomiSide_num='vm_obj.DSTnum'
        DomiSide='SRC'
        unDomiSide_num__set = 'DST_num__set'
        DomiSide_num__set = 'SRC_num__set'
        DomiMetric='VM_cl2.upBSratio'
    else:
        assert(0)

    DST_num__set = G.DST_host__set & G.GPNum_to_host__dict[GPNum]
    SRC_num__set = G.SRC_host__set & G.GPNum_to_host__dict[GPNum]
        
    ### unDominant host set 
    print 'function.py  func_SS()  unDominant host set'
    for host_num in eval(unDomiSide_num__set):
        host_obj = G.all_host__dict[host_num]
        
        tuple__list = []   # store tuple (vm_obj, feasible_rate)
        for vm_num in host_obj.reg_q__Set:
            vm_obj = G.all_VM__dict[vm_num]
            print 'function.py  func_SS()  unDominant host set  speed_checking 1'
            result, miniRate = vm_obj.speed_checking('full', DomiSide) #miniRate=dominant side rate
            if result == 'success':
                tuple__list.append( (vm_obj, miniRate) )
        
        seq_vm_obj__list = []
        if (sort_mode=='ascending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1])   #from small to large
        elif (sort_mode == 'descending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1], reverse = True)   #from large to small
        elif (sort_mode == 'random'):
            seq_vm_obj__list = random.sample(tuple__list, len(tuple__list))
        else:
            assert (0)
        
        # inv__list = seq_vm_obj__list[::-1]
        for vm_obj,  miniRate in seq_vm_obj__list:
            print 'function.py  func_SS()  unDominant host set  speed_checking 2'
            tmp_result, tmp_miniRate = vm_obj.speed_checking('full', DomiSide)
            if tmp_result == 'success':
                vm_obj.assign_VM_BW(tmp_miniRate)
                temp_set = set([vm_obj.vm_num]) # if assign, delete from seq__list
                host_obj.reg_q__Set = host_obj.reg_q__Set - temp_set

    ### Dominant host set
    print 'function.py  func_SS()  Dominant host set'
    for host_num in eval(DomiSide_num__set):
        host_obj = G.all_host__dict[host_num]
        seq_vm_obj__list = sorted(host_obj.GPNum_to_VM__dict[GPNum], key=lambda VM_cl2: eval(DomiMetric))
        
        ### only waiting for the first SRC
        for vm_obj in seq_vm_obj__list:
            print 'function.py  func_SS()  Dominant host set  speed_checking 1'
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = DomiSide)
            if result == 'success':
                vm_obj.assign_VM_BW(miniRate)
                
                break
            else: #register
                regHost_num = eval(unDomiSide_num)
                G.all_host__dict[regHost_num].reg_q__Set.add(vm_obj.vm_num)
                break
                