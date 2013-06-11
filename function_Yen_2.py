import basic

def func_SS_modified(G,finish_vm):
    print 'func_SS' ,'finish_vm = ', finish_vm
    SRC_num = G.all_VM__dict[finish_vm].SRCnum
    DST_num = G.all_VM__dict[finish_vm].DSTnum
    SRC_host = G.all_host__dict[SRC_num]
    DST_host = G.all_host__dict[DST_num]

    # for vm_obj in G.all_host__dict[0].GPNum_to_VM__dict[2]:
        # print "???",vm_obj.vm_num
    seq_vm_obj__list = sorted(DST_host.GPNum_to_VM__dict[1], key=lambda VM_cl2: VM_cl2.dnBSratio)

    for vm_obj in seq_vm_obj__list:
        result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'DST' )
        if result == 'success':
            # print '1#######',vm_obj.vm_num
            vm_obj.assign_VM_BW(miniRate)
            break
            
    # for vm_obj in SRC_host.GPNum_to_VM__dict[2]:
        # print "@@@",vm_obj.vm_num
    seq_vm_obj__list = sorted(SRC_host.GPNum_to_VM__dict[2], key=lambda VM_cl2: VM_cl2.upSBratio)
    
    for vm_obj in seq_vm_obj__list:
        result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'SRC' )
        if result == 'success':
            # print '2#######',vm_obj.vm_num
            vm_obj.assign_VM_BW(miniRate)
            break
