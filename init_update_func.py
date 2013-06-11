import basic

def update_SetNum_GPNum_to_vm_to_host(G):
    print 'update_SetNum_GPNum_to_vm_to_host()'
    print 'all_VM__dict len', len(G.all_VM__dict)
    for vm_num,vm_obj in G.all_VM__dict.items():        # categorizing all_VM into 3 Sets
        vm_set_num = vm_obj.get_set_num()
        G.SetNum_to_VM__dict[vm_set_num].add(vm_num)
        G.SetNum_to_host__dict[vm_set_num].add(vm_obj.SRCnum)
        G.SetNum_to_host__dict[vm_set_num].add(vm_obj.DSTnum)
        G.all_host__dict[vm_obj.SRCnum].waiting_vm__set.add(vm_num)
        G.all_host__dict[vm_obj.DSTnum].waiting_vm__set.add(vm_num)
        if vm_set_num==1:
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[1].add(vm_obj)
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[1].add(vm_obj)
        elif vm_set_num==2 or vm_set_num ==3:
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[2].add(vm_obj)
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[2].add(vm_obj) 
        else :
            assert(0)
        G.SRC_host__set.add(vm_obj.SRCnum)
        G.DST_host__set.add(vm_obj.DSTnum)
        print 'vm', vm_num, 'SRC', vm_obj.SRCnum, 'DST', vm_obj.DSTnum
    print 'SRC_host__set', G.SRC_host__set
    print 'DST_host__set', G.DST_host__set
    
    G.GPNum_to_VM__dict[1] = G.SetNum_to_VM__dict[1]  # categorizing GPs by 3 Sets
    G.GPNum_to_VM__dict[2] = G.SetNum_to_VM__dict[2] | G.SetNum_to_VM__dict[3]
    G.GPNum_to_host__dict[1] = G.SetNum_to_host__dict[1]
    G.GPNum_to_host__dict[2] = G.SetNum_to_host__dict[2] | G.SetNum_to_host__dict[3] - G.SetNum_to_host__dict[1]
    print 'update_SetNum_GPNum_to_vm_to_host()'
    
    print '\tSet1_host', G.SetNum_to_host__dict[1]
    print '\tSet2_host', G.SetNum_to_host__dict[2]
    print '\tSet3_host', G.SetNum_to_host__dict[3]
    
    print '\tSet1_VM', G.SetNum_to_VM__dict[1]
    print '\tSet2_VM', G.SetNum_to_VM__dict[2]
    print '\tSet3_VM', G.SetNum_to_VM__dict[3]

    print '\tGP1_host', G.GPNum_to_host__dict[1]
    print '\tGP2_host', G.GPNum_to_host__dict[2]
    
    print '\tGP1_VM', G.GPNum_to_VM__dict[1]
    print '\tGP2_VM', G.GPNum_to_VM__dict[2], '\n'


def func_SS_INIT(G):
    ### Need assignment, ex vmm bw, host bw ...
    ### Need calculate SB ratio

    update_SetNum_GPNum_to_vm_to_host(G)
    
    DST_GP1 = G.DST_host__set & G.GPNum_to_host__dict[1]   # find those destination host in Group 1
    print 'init_update_func.func_SS_INIT():  DST_GP1', DST_GP1
    for host_num in DST_GP1:
        host_obj = G.all_host__dict[host_num]
        seq_vm_obj__list = sorted(host_obj.GPNum_to_VM__dict[1], key=lambda VM_cl2: VM_cl2.dnSBratio, reverse = True )
        
        for vm_obj in seq_vm_obj__list:
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'DST')
            if result == 'success':
                vm_obj.assign_VM_BW(miniRate)
                break
            else:
                SRCnum = vm_obj.SRCnum
                G.all_host__dict[SRCnum].reg_q__Set.add(vm_obj.vm_num)
                break


    SRC_GP2 = G.SRC_host__set & G.GPNum_to_host__dict[2]    #find those source host in Group 2
    print 'init_update_func.func_SS_INIT():  SRC_GP2', SRC_GP2
    for host_num in SRC_GP2:
        host_obj = G.all_host__dict[host_num]
        ### mika
        seq_vm_obj__list = sorted(host_obj.GPNum_to_VM__dict[2], key=lambda VM_cl2: VM_cl2.upSBratio )
        
        for vm_obj in seq_vm_obj__list:
            result, miniRate = vm_obj.speed_checking(BW_mode = 'full', domi_node = 'SRC')
            if result == 'success':
                vm_obj.assign_VM_BW(miniRate)
                break
            else:
                DSTnum = vm_obj.DSTnum
                G.all_host__dict[DSTnum].reg_q__Set.add(vm_obj.vm_num)
                break


def func_SS_update_ongoing(G,finish_vm):
    SRC_num = G.all_VM__dict[finish_vm].SRCnum
    DST_num = G.all_VM__dict[finish_vm].DSTnum
    SRC_host = SRCobj = G.all_host__dict[SRC_num]
    DST_host = DSTobj = G.all_host__dict[DST_num]
    
    fin_vm_set_num = G.all_VM__dict[finish_vm].set_num
    vm_obj = G.all_VM__dict[finish_vm]
    print 'init_update_func.py  func_SS_update_ongoing(), finish_vm=', finish_vm, 'set_num', fin_vm_set_num

    if fin_vm_set_num==1:
        SRCobj.GPNum_to_VM__dict[1] -= set([vm_obj])
        DSTobj.GPNum_to_VM__dict[1] -= set([vm_obj])
    elif fin_vm_set_num ==2 or fin_vm_set_num ==3:
        SRCobj.GPNum_to_VM__dict[2] -= set([vm_obj])
        DSTobj.GPNum_to_VM__dict[2] -= set([vm_obj])
    else :
        assert(0)

    G.SetNum_to_VM__dict[fin_vm_set_num] -= set([finish_vm])
    G.SetNum_to_host__dict[fin_vm_set_num] -= set([SRC_num])
    G.SetNum_to_host__dict[fin_vm_set_num] -= set([DST_num])
    
    for vm_num in SRC_host.waiting_vm__set:
        vm_obj = G.all_VM__dict[vm_num]
        prev_vm_set_num = vm_obj.set_num
        now_vm_set_num = vm_obj.get_set_num()          #recalculate to catgorize sets
        if prev_vm_set_num != now_vm_set_num:
            G.SetNum_to_VM__dict[prev_vm_set_num] -= set([vm_num])
            G.SetNum_to_host__dict[prev_vm_set_num] -= set([vm_obj.SRCnum])
            G.SetNum_to_host__dict[prev_vm_set_num] -= set([vm_obj.DSTnum])
            ###
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[1] -= set([vm_obj])
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[1] -= set([vm_obj])
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[2] -= set([vm_obj])
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[2] -= set([vm_obj])
            ###
            G.SetNum_to_VM__dict[now_vm_set_num].add(vm_num)
            if now_vm_set_num==1:
                G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[1].add(vm_obj)
                G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[1].add(vm_obj)
            elif now_vm_set_num==2 or now_vm_set_num==3:
                G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[2].add(vm_obj)
                G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[2].add(vm_obj) 
            else :
                assert(0)
                
    for vm_num in SRC_host.waiting_vm__set:
        vm_obj = G.all_VM__dict[vm_num]
        vm_set_num = vm_obj.set_num
        G.SetNum_to_host__dict[vm_set_num].add(vm_obj.SRCnum)
        G.SetNum_to_host__dict[vm_set_num].add(vm_obj.DSTnum)

    for vm_num in DST_host.waiting_vm__set:
        vm_obj = G.all_VM__dict[vm_num]
        prev_vm_set_num = vm_obj.set_num
        now_vm_set_num = vm_obj.get_set_num()          #recalculate to catgorize sets
        if prev_vm_set_num != now_vm_set_num:
            G.SetNum_to_VM__dict[prev_vm_set_num] -= set([vm_num])
            G.SetNum_to_host__dict[prev_vm_set_num] -= set([vm_obj.SRCnum])
            G.SetNum_to_host__dict[prev_vm_set_num] -= set([vm_obj.DSTnum])
            ###
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[1] -= set([vm_obj])
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[1] -= set([vm_obj])
            G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[2] -= set([vm_obj])
            G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[2] -= set([vm_obj])
            ###
            G.SetNum_to_VM__dict[now_vm_set_num].add(vm_num)
            if now_vm_set_num==1:
                G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[1].add(vm_obj)
                G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[1].add(vm_obj)
            elif now_vm_set_num==2 or now_vm_set_num==3:
                G.all_host__dict[vm_obj.SRCnum].GPNum_to_VM__dict[2].add(vm_obj)
                G.all_host__dict[vm_obj.DSTnum].GPNum_to_VM__dict[2].add(vm_obj) 
            else :
                assert(0)
    
        for vm_num in DST_host.waiting_vm__set:
            vm_obj = G.all_VM__dict[vm_num]
            vm_set_num = vm_obj.set_num
            G.SetNum_to_host__dict[vm_set_num].add(vm_obj.SRCnum)
            G.SetNum_to_host__dict[vm_set_num].add(vm_obj.DSTnum)
            
    G.GPNum_to_VM__dict[1] = G.SetNum_to_VM__dict[1]  # categorizing GPs by 3 Sets
    G.GPNum_to_VM__dict[2] = G.SetNum_to_VM__dict[2] | G.SetNum_to_VM__dict[3]
    G.GPNum_to_host__dict[1] = G.SetNum_to_host__dict[1]
    G.GPNum_to_host__dict[2] = G.SetNum_to_host__dict[2] | G.SetNum_to_host__dict[3] - G.SetNum_to_host__dict[1]
    print 'func_SS_update_ongoing()'
    
    print '\tSet1_host', G.SetNum_to_host__dict[1]
    print '\tSet2_host', G.SetNum_to_host__dict[2]
    print '\tSet3_host', G.SetNum_to_host__dict[3]
    
    print '\tSet1_VM', G.SetNum_to_VM__dict[1]
    print '\tSet2_VM', G.SetNum_to_VM__dict[2]
    print '\tSet3_VM', G.SetNum_to_VM__dict[3]

    print '\tGP1_host', G.GPNum_to_host__dict[1]
    print '\tGP2_host', G.GPNum_to_host__dict[2]
    
    print '\tGP1_VM', G.GPNum_to_VM__dict[1]
    print '\tGP2_VM', G.GPNum_to_VM__dict[2], '\n'
