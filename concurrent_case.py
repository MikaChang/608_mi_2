import basic

def func_Concurrent(G,initFlag):
    ### Need assignment, ex vmm bw, host bw ...
    ### Need calculate SB ratio
    totalVM = 0
    readyVM = 0
    bool__dict = []        # vm_num and status, status -1 == completed, status 0 == still running, status 1 == ok
    ### need modification
    bwStep = linkBW*0.001
    ###


    ###
    #need update RemainSize
    ###

    for vm_num,vm_obj in G.all_VM__dict.items():        
        bool__dict[vm_num] = -1        
        if vm_obj.status == waiting or vm_obj.status == sending:
            SRCobj = G.all_host__dict[vm_obj.SRCnum]
            DSTobj = G.all_host__dict[vm_obj.DSTnum]
            
            SRCobj.upRBW_tmp = SRCobj.upRBW
            DSTobj.dnRBW_tmp = DSTobj.dnRBW
         
            if initFlag == True:
                if vm_obj.migration_mode == 'StopNCopy':
                    SRCobj.upRBW_tmp += vm_obj.upSBW    # StopNCopy mode!!!
            else :
                SRCobj.upRBW_tmp += vm_obj.latest_data_rate
                DSTobj.dnRBW_tmp += vm_obj.latest_data_rate 
            bool__dict[vm_num] = 0
            vm_obj.tmp_rate = 0
            totalVM+=1


    while readyVM < totalVM:
        for vm_num,status in bool__dict.items():
            if status == 0: 
                vm_obj = G.all_VM__dict[vm_num]
                SRCobj = G.all_host__dict[vm_obj.SRCnum]
                DSTobj = G.all_host__dict[vm_obj.DSTnum]
                if SRCobj.upRBW_tmp >= bwStep & DSTobj.dnRBW_tmp >= bwStep:
                    vm_obj.tmp_rate += bwStep
                    SRCobj.upRBW_tmp -= bwStep
                    DSTobj.dnRBW_tmp -= bwStep
                else :
                    vm_obj.tmp_rate += min(SRCobj.upRBW_tmp,DSTobj.dnRBW_tmp)
                    SRCobj.upRBW_tmp -= min(SRCobj.upRBW_tmp,DSTobj.dnRBW_tmp)
                    DSTobj.dnRBW_tmp -= min(SRCobj.upRBW_tmp,DSTobj.dnRBW_tmp)
                    bool__List[vm_num] = 1
                    readyVM +=1
                    
    for vm_num,status in bool__dict.items():
        if status == 1:
            vm_obj = G.all_VM__dict[vm_num]
            if initFlag == True:
                vm_obj.assign_VM_BW(vm_obj.tmp_rate)
            else :
                if vm_obj.tmp_rate != vm_obj.latest_data_rate:
                    vm_obj.adjust_VM_BW(vm_obj.tmp_rate)


            #if self.migration_start_time == 0:
            ##    self.migration_start_time = self.G.now
            ##self.last_migration_event_time = self.G.now
            ##self.G.E.list.insert(event_obj)


