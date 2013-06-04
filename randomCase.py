import basic
import init_parameter

def func_ran_disjoint_init(G):
    print 'func_ran_disjoint_init, randomCase.py'
    #disjoint_VM__set
    #non_disjoint__set
    #waiting__set
    disjoint_host__set = set()
    
    for vm_num, vm_obj in G.all_VM__dict.items():
        if vm_obj.SRCnum not in disjoint_host__set and vm_obj.DSTnum not in disjoint_host__set:
            G.disjoint_VM__set.add(vm_num)
            disjoint_host__set.add(vm_obj.SRCnum)
            disjoint_host__set.add(vm_obj.DSTnum)
    
    for vm_num in G.disjoint_VM__set:
        vm_obj = G.all_VM__dict[vm_num]
        result, dataRate = vm_obj.speed_checking('partial',None)
        vm_obj.assign_VM_BW(dataRate)
            
    tmp_set = set(G.all_VM__dict.keys())
    tmp_set = tmp_set - G.disjoint_VM__set
    
    for vm_num in tmp_set:
        vm_obj = G.all_VM__dict[vm_num]
        result, dataRate = vm_obj.speed_checking('partial',None)
        if result == 'fail':
            continue
        else:
            vm_obj.assign_VM_BW(dataRate)
            G.non_disjoint__set.add(vm_num)
            
    G.waiting__set = set(G.all_VM__dict.keys())
    G.waiting__set = G.waiting__set - G.disjoint_VM__set - G.non_disjoint__set

def func_ran_disjoint_ongoing(G,finish_vm):
    SRC_num = G.all_VM__dict[finish_vm].SRCnum
    DST_num = G.all_VM__dict[finish_vm].DSTnum
    SRC_host = G.all_host__dict[SRC_num]
    DST_host = G.all_host__dict[DST_num]
    
    G.disjoint_VM__set.discard(finish_vm)
    G.non_disjoint__set.discard(finish_vm)
    
    SRC_relatedVM_non_disjoint = set([ ])
    SRC_relatedVM_waiting = set([ ])
    DST_relatedVM_non_disjoint = set([ ])
    DST_relatedVM_waiting = set([ ])
    
    ### Categorizing
    for vm_num in G.non_disjoint__set:
        if G.all_VM__dict[vm_num].SRCnum == SRC_num:
            SRC_relatedVM_non_disjoint.add(vm_num)
        if G.all_VM__dict[vm_num].DSTnum == DST_num:
            DST_relatedVM_non_disjoint.add(vm_num)
            
    for vm_num in G.waiting__set:
        if G.all_VM__dict[vm_num].SRCnum == SRC_num:
            SRC_relatedVM_waiting.add(vm_num)
        if G.all_VM__dict[vm_num].DSTnum == DST_num:
            DST_relatedVM_waiting.add(vm_num)
    ###
    
    ### SRC case
    
    for vm_num in SRC_relatedVM_non_disjoint:
        vm_obj = G.all_VM__dict[vm_num]
        result, dataRate = vm_obj.speed_checking('partial',None)
        if result == 'success':
            vm_obj.adjust_VM_BW(dataRate)
        elif SRC_host.upRBW <= ACCEPTABLE_MINI_VMM_DATA_RATE:
            break
            
    for vm_num in SRC_relatedVM_waiting:
        vm_obj = G.all_VM__dict[vm_num]
        result, dataRate = vm_obj.speed_checking('partial',None)
        if result == 'success':
            vm_obj.assign_VM_BW(dataRate)
            G.non_disjoint__set.add(vm_num)

    ### DST case
    DST_BW_EXHAUST = False
    
    for vm_num in DST_relatedVM_non_disjoint:
        vm_obj = G.all_VM__dict[vm_num]
        result, dataRate = vm_obj.speed_checking('partial',None)
        if result == 'success':
            vm_obj.adjust_VM_BW(dataRate)
        elif DST_host.dnRBW <= ACCEPTABLE_MINI_VMM_DATA_RATE:
            DST_BW_EXHAUST = True
            break
            
    if DST_BW_EXHAUST == False:
        for vm_num in DST_relatedVM_waiting:
            vm_obj = G.all_VM__dict[vm_num]
            result, dataRate = vm_obj.speed_checking('partial',None)
            if result == 'success':
                vm_obj.assign_VM_BW(dataRate)
                G.non_disjoint__set.add(vm_num)
            elif DST_host.dnRBW <= ACCEPTABLE_MINI_VMM_DATA_RATE:
                DST_BW_EXHAUST = True
                break
            