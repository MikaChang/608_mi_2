import basic
from init_parameter import SET__set, GP__set, SLOTTIME, ACCEPTABLE_MINI_VMM_DATA_RATE, RATE_PRECISION

def func_Concurrent_Init(G):
    ### Need assignment, ex vmm bw, host bw ...
    ### Need calculate SB ratio
    totalVM = 0
    readyVM = 0
    bool__dict = dict()        # vm_num and status, status -1 == completed, status 0 == still running, status 1 == ok
    ### need modification
    # bwStep = linkBW*0.001
    bwStep = 0.01
    # bwStep = 1
    ###
    
    for vm_num,vm_obj in G.all_VM__dict.items():        
        bool__dict[vm_num] = -1
        SRCobj = G.all_host__dict[vm_obj.SRCnum]
        DSTobj = G.all_host__dict[vm_obj.DSTnum]
        SRCobj.upRBW_tmp = SRCobj.upRBW
        DSTobj.dnRBW_tmp = DSTobj.dnRBW

    for vm_num,vm_obj in G.all_VM__dict.items():
        SRCobj = G.all_host__dict[vm_obj.SRCnum]
        if G.migration_mode == 'StopNCopy':
            SRCobj.upRBW_tmp += vm_obj.upSBW
        bool__dict[vm_num] = 0
        vm_obj.tmp_rate = 0
        totalVM+=1

    while readyVM < totalVM:
        for vm_num,status in bool__dict.items():
            if status == 0: 
                vm_obj = G.all_VM__dict[vm_num]
                SRCobj = G.all_host__dict[vm_obj.SRCnum]
                DSTobj = G.all_host__dict[vm_obj.DSTnum]
                if SRCobj.upRBW_tmp >= 2 * bwStep and DSTobj.dnRBW_tmp >= 2* bwStep:
                    vm_obj.tmp_rate += bwStep
                    SRCobj.upRBW_tmp -= bwStep
                    DSTobj.dnRBW_tmp -= bwStep
                else :
                    # minRate = min(SRCobj.upRBW_tmp,DSTobj.dnRBW_tmp) - RATE_PRECISION
                    # vm_obj.tmp_rate += minRate
                    # SRCobj.upRBW_tmp -= minRate
                    # DSTobj.dnRBW_tmp -= minRate
                    bool__dict[vm_num] = 1
                    readyVM +=1
                    
    for vm_num,status in bool__dict.items():
        if status==1:
            vm_obj = G.all_VM__dict[vm_num]
            assert(vm_obj.status == 'waiting')
            
    for vm_num,status in bool__dict.items():
        if status == 1:
            vm_obj = G.all_VM__dict[vm_num]
            vm_obj.assign_VM_BW(vm_obj.tmp_rate)
            #assert(vm_obj.tmp_rate > 0), vm_obj.tmp_rate
            #vm_obj.concurrent_adjust_VM_BW(vm_obj.tmp_rate)
            #if self.migration_start_time == 0:
            ##    self.migration_start_time = self.G.now
            ##self.last_migration_event_time = self.G.now
            ##self.G.E.list.insert(event_obj)
            
def func_Concurrent_Ongoing(G,finish_vm):
    totalVM = 0
    readyVM = 0
    bool__dict = dict()
    bwStep = 0.01
    
    for vm_num,vm_obj in G.all_VM__dict.items():
        assert(vm_obj.status != 'waiting')
        if vm_obj.status == 'sending':
            vm_obj.concurrent_resetVM_BW()
    
    vm_obj = G.all_VM__dict[finish_vm]
    SRCobj = G.all_host__dict[vm_obj.SRCnum]
    DSTobj = G.all_host__dict[vm_obj.DSTnum]
    DSTobj.upRBW -= vm_obj.upSBW
    DSTobj.dnRBW -= vm_obj.dnSBW
    
    # # # release the BW used by vm service at src
    if G.migration_mode == 'PreCopy':
        SRCobj.upRBW += vm_obj.upSBW    # PreCopy mode!!!
        SRCobj.dnRBW += vm_obj.dnSBW    # PreCopy mode!!!
    else:
        assert (G.migration_mode == 'StopNCopy')
    vm_obj.next_status()
    vm_obj.migration_over_time = G.now
    vm_obj.assert_host_RBW()
    
    for vm_num,vm_obj in G.all_VM__dict.items():        
        bool__dict[vm_num] = -1
        if vm_obj.status == 'sending':
            SRCobj = G.all_host__dict[vm_obj.SRCnum]
            DSTobj = G.all_host__dict[vm_obj.DSTnum]
            SRCobj.upRBW_tmp = SRCobj.upRBW
            DSTobj.dnRBW_tmp = DSTobj.dnRBW
            bool__dict[vm_num] = 0
            vm_obj.tmp_rate = 0
            totalVM+=1
            
    while readyVM < totalVM:
        for vm_num,status in bool__dict.items():
            if status == 0: 
                vm_obj = G.all_VM__dict[vm_num]
                SRCobj = G.all_host__dict[vm_obj.SRCnum]
                DSTobj = G.all_host__dict[vm_obj.DSTnum]
                if SRCobj.upRBW_tmp >= 2 * bwStep and DSTobj.dnRBW_tmp >= 2* bwStep:
                    vm_obj.tmp_rate += bwStep
                    SRCobj.upRBW_tmp -= bwStep
                    DSTobj.dnRBW_tmp -= bwStep
                else :
                    # minRate = min(SRCobj.upRBW_tmp,DSTobj.dnRBW_tmp) - RATE_PRECISION
                    # vm_obj.tmp_rate += minRate
                    # SRCobj.upRBW_tmp -= minRate
                    # DSTobj.dnRBW_tmp -= minRate
                    bool__dict[vm_num] = 1
                    readyVM +=1
                    
    for vm_num,status in bool__dict.items():
        if status==1:
            vm_obj = G.all_VM__dict[vm_num]
            assert(vm_obj.status == 'sending')
            
    for vm_num,status in bool__dict.items():
        if status == 1:
            vm_obj = G.all_VM__dict[vm_num]
            assert(vm_obj.tmp_rate>0)
            vm_obj.concurrent_adjust_VM_BW(vm_obj.tmp_rate)