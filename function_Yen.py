import basic
import random

def func_SS(G, GPNum, sort_mode,finish_vm):
    print 'func_SS' ,GPNum ,'finish_vm = ', finish_vm
    SRC_num = G.all_VM__dict[finish_vm].SRCnum
    DST_num = G.all_VM__dict[finish_vm].DSTnum
    SRC_host = G.all_host__dict[SRC_num]
    DST_host = G.all_host__dict[DST_num]
    print DST_host.upRBW, DST_host.dnRBW
    # for vm_obj in G.all_host__dict[0].GPNum_to_VM__dict[2]:
        # print "???",vm_obj.vm_num
    if GPNum == 1:
        seq_vm_obj__list = sorted(DST_host.GPNum_to_VM__dict[1], key=lambda VM_cl2: VM_cl2.dnBSratio)

        for vm_obj in seq_vm_obj__list:
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'DST' )
            if result == 'success':
                # print '1#######',vm_obj.vm_num
                vm_obj.assign_VM_BW(miniRate)
                break
            else:
                G.all_host__dict[vm_obj.SRCnum].reg_q__Set.add(vm_obj.vm_num)
                break
        
        tuple__list = []
        for vm_num in SRC_host.reg_q__Set:
            vm_obj = G.all_VM__dict[vm_num]
            result, miniRate = vm_obj.speed_checking('full', 'SRC') #miniRate=dominant side rate
            if result == 'success':
                tuple__list.append( (vm_obj, miniRate) )
        
        seq_vm_obj__list = []
        if (sort_mode=='ascending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1]) 
        elif (sort_mode == 'descending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1], reverse = True) 
        elif (sort_mode == 'random'):
            seq_vm_obj__list = random.sample(tuple__list, len(tuple__list))
        else:
            assert (0)
        
        for vm_obj,  miniRate in seq_vm_obj__list:
            result, dataRate = vm_obj.speed_checking('full', 'SRC')
            if result == 'success':
                # print '1#######',vm_obj.vm_num
                vm_obj.assign_VM_BW(dataRate)
    elif GPNum==2:
        # for vm_obj in SRC_host.GPNum_to_VM__dict[2]:
            # print "@@@",vm_obj.vm_num
        seq_vm_obj__list = sorted(SRC_host.GPNum_to_VM__dict[2], key=lambda VM_cl2: VM_cl2.upSBratio)
        
        for vm_obj in seq_vm_obj__list:
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'SRC' )
            if result == 'success':
                # print '2#######',vm_obj.vm_num
                vm_obj.assign_VM_BW(miniRate)
                break
            else:
                G.all_host__dict[vm_obj.DSTnum].reg_q__Set.add(vm_obj.vm_num)
                break
        
        tuple__list = []
        for vm_num in DST_host.reg_q__Set:
            vm_obj = G.all_VM__dict[vm_num]
            result, miniRate = vm_obj.speed_checking('full', 'DST') #miniRate=dominant side rate
            if result == 'success':
                tuple__list.append( (vm_obj, miniRate) )
        
        seq_vm_obj__list = []
        if (sort_mode=='ascending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1]) 
        elif (sort_mode == 'descending'):
            seq_vm_obj__list = sorted(tuple__list, key = lambda tup: tup[1], reverse = True) 
        elif (sort_mode == 'random'):
            seq_vm_obj__list = random.sample(tuple__list, len(tuple__list))
        else:
            assert (0)
        
        for vm_obj,  miniRate in seq_vm_obj__list:
            result, dataRate = vm_obj.speed_checking('full', 'DST')
            if result == 'success':
                # print '2#######',vm_obj.vm_num
                vm_obj.assign_VM_BW(dataRate)
    else:
        assert(0)