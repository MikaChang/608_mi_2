import math
import random
import copy

from basic import *

# # # ^^^random.randint^^^ ==> ^^^random.randint^^^

def migr_gen_C(type, vm_num_count, src_num, all_host__dict, all_VM__dict, src__dict):
    
    # # # mika for debug
    test_all_host__dict = copy.deepcopy(all_host__dict)
    
    
    if type == 'vmFirst':
        vm__list = range(vm_num_count) # all the vm_num
        ### sorted by each VM's sigma+upSBW+dnSBW
        vm__list = sorted(vm__list, key = lambda vm_num: all_VM__dict[vm_num].sigma + all_VM__dict[vm_num].upSBW + all_VM__dict[vm_num].dnSBW, reverse = True)
        
        dst__list = range(src_num, len(all_host__dict)) # all the DSTnum
        ### sorted by each host's sigma+upBW+dnBW
        dst__list = sorted(dst__list, key = lambda host_num: all_host__dict[host_num].upBW + all_host__dict[host_num].dnBW + all_host__dict[host_num].sigma, reverse = True)
        
        for aVM in vm__list:
            vm_obj = all_VM__dict[aVM]
            for aHost in dst__list:
                dst_obj = all_host__dict[aHost]
                
                vm_upSBW = vm_obj.upSBW
                vm_dnSBW = vm_obj.dnSBW
                vm_sigma = vm_obj.sigma
                
                
                if (dst_obj.upBW_tmp + vm_upSBW < dst_obj.BWC) & \
                (dst_obj.dnBW_tmp + vm_dnSBW < dst_obj.BWC) & \
                (dst_obj.sigma_tmp + vm_sigma < dst_obj.sigmaC):
                    vm_obj.DSTnum = aHost
                    # # #print_out every info in vm_obj
                    # vm_obj.print_out()
                    
                    # record the future service requirement in DST host    1)# dst_obj.upBW_tmp    2)# dst_obj.dnBW_tmp    3)# dst_obj.sigma_tmp
                    dst_obj.upBW_tmp += vm_upSBW
                    dst_obj.dnBW_tmp += vm_dnSBW
                    dst_obj.sigma_tmp += vm_sigma                    
                    
                    dst_obj.Final_upRBW -= vm_upSBW
                    dst_obj.Final_dnRBW -= vm_dnSBW

                    # # # update the SRC Final RBW
                    all_host__dict[vm_obj.SRCnum].Final_upRBW += vm_upSBW
                    all_host__dict[vm_obj.SRCnum].Final_dnRBW += vm_dnSBW
                    
                    # # # mika debug...
                    vm_obj.VM_god_migration(test_all_host__dict)
                    
                    break
                else:
                    continue
    
    elif type == 'srcFirst':
        ### vm_num_count, src_num, all_host__dict, all_VM__dict, src__dict
        vm__list = range(vm_num_count) 
        
        src_score__list = list()
        for src_idx in range(src_num):
            score = 0
            for vm_idx in src__dict[src_idx]:
                vm_obj = all_VM__dict[vm_idx]
                score += vm_obj.sigma + vm_obj.upSBW + vm_obj.dnSBW
            src_score__list.append((src_idx, score))
        src_score__list = sorted(src_score__list, key = lambda src: src[1], reverse = True)
        
        
        dst__list = range(src_num, len(all_host__dict)) # all the DSTnum
        ### sorted by each host's sigma+upBW+dnBW
        dst__list = sorted(dst__list, key = lambda host_num: all_host__dict[host_num].upBW + all_host__dict[host_num].dnBW + all_host__dict[host_num].sigma, reverse = True)
        
        for src_idx, score in src_score__list:
            tmp_vm__list = sorted(src__dict[src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].upSBW + all_VM__dict[vm_idx].dnSBW + all_VM__dict[vm_idx].sigma, reverse = True)
            for aVM in tmp_vm__list:
                vm_obj = all_VM__dict[aVM]
                for aHost in dst__list:
                    dst_obj = all_host__dict[aHost]
                    
                    vm_upSBW = vm_obj.upSBW
                    vm_dnSBW = vm_obj.dnSBW
                    vm_sigma = vm_obj.sigma
                    
                    
                    if (dst_obj.upBW_tmp + vm_upSBW < dst_obj.BWC) & \
                    (dst_obj.dnBW_tmp + vm_dnSBW < dst_obj.BWC) & \
                    (dst_obj.sigma_tmp + vm_sigma < dst_obj.sigmaC):
                        vm_obj.DSTnum = aHost
                        
                        # record the future service requirement in DST host    1)# dst_obj.upBW_tmp    2)# dst_obj.dnBW_tmp    3)# dst_obj.sigma_tmp
                        dst_obj.upBW_tmp += vm_upSBW
                        dst_obj.dnBW_tmp += vm_dnSBW
                        dst_obj.sigma_tmp += vm_sigma                    
                        
                        
                        
                        # # #print_out every info in vm_obj
                        # vm_obj.print_out()
                        dst_obj.Final_upRBW -= vm_upSBW
                        dst_obj.Final_dnRBW -= vm_dnSBW

                        
                        # # # update the SRC Final RBW
                        all_host__dict[vm_obj.SRCnum].Final_upRBW += vm_upSBW
                        all_host__dict[vm_obj.SRCnum].Final_dnRBW += vm_dnSBW
                        
                        break
                    else:
                        continue
    
    
    else:
        assert(0)
    
    for aVM in vm__list:
        if all_VM__dict[aVM].DSTnum == None: # 'There is a VM havnt alloc to DST since all the DSTs are full'
            return (False, None, None)
    
    
    # # # mika debug...
    for key, host_obj in test_all_host__dict.items():
        host_obj.assert_RBW()
    
    return True

    
    
def migr_gen_LB(vm_sel_mode, vm_sigma_range, src_num, all_host__dict, all_VM__dict, src__dict):
    
        # # # mika for debug
    test_all_host__dict = copy.deepcopy(all_host__dict)
    
    # sort the SRC/DST by sigma
    src__list = range(src_num)
    src__list = sorted(src__list, key = lambda host_idx: all_host__dict[host_idx].sigma_tmp, reverse = True)
    dst__list = range(src_num, len(all_host__dict))
    dst__list = sorted(dst__list, key = lambda host_idx: all_host__dict[host_idx].sigma_tmp)
    
    # target_host initialization
    target_src_idx = src__list[0] # the fullest SRC
    target_dst_idx = dst__list[0] # the emptiest DST
    target_src = all_host__dict[target_src_idx]
    target_dst = all_host__dict[target_dst_idx]
    
    # # tmp_vm__list initialization
    # if vm_sel_mode == 'ascending':
        # tmp_vm__list = sorted(src__dict[target_src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma)
    # elif vm_sel_mode == 'descending':
        # tmp_vm__list = sorted(src__dict[target_src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma, reverse = True)
    # elif vm_sel_mode == 'random':
        # tmp_vm__list = random.sample(src__dict[target_src_idx], len(src__dict[target_src_idx]))
    # else:
        # assert(0), 'vm_sel_mode error'
    
    migrated_vm__set = set()
    
    while (target_src.sigma_tmp - target_dst.sigma_tmp) > vm_sigma_range[1]:
        
        
        src_idx = src__list[0] # the fullest SRC
        dst_idx = dst__list[0] # the emptiest DST
        dst_obj = all_host__dict[dst_idx]
        src_obj = all_host__dict[src_idx]
        
        print 'src_idx = ', src_idx
        print 'src_idx = ', src__list[0], 'sigma = ', target_src.sigma_tmp
        print 'dst_idx = ', dst__list[0], 'sigma = ', target_dst.sigma_tmp
        
        print 'difference = ', target_src.sigma_tmp - target_dst.sigma_tmp
        print 'sigma range = ', vm_sigma_range[1]
        
        # if vm_sel_mode == 'ascending':
            # tmp_vm__list = sorted(src__dict[src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma)
        # elif vm_sel_mode == 'descending':
            # tmp_vm__list = sorted(src__dict[src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma, reverse = True)
        # elif vm_sel_mode == 'random':
            # tmp_vm__list = random.sample(src__dict[src_idx], len(src__dict[src_idx]))
        # else:
            # assert(0), 'vm_sel_mode error'
        
        # # select a VM
        # print 'length of tmp_vm__list = ', len(tmp_vm__list)
        # vm_obj_idx = tmp_vm__list[0]
        # del tmp_vm__list[0]
        # vm_obj = all_VM__dict[vm_obj_idx]
        
        if vm_sel_mode == 'ascending':
            src__dict[src_idx] = sorted(src__dict[src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma)
        elif vm_sel_mode == 'descending':
            src__dict[src_idx] = sorted(src__dict[src_idx], key = lambda vm_idx: all_VM__dict[vm_idx].sigma, reverse = True)
        elif vm_sel_mode == 'random':
            src__dict[src_idx] = random.sample(src__dict[src_idx], len(src__dict[src_idx]))
        else:
            assert(0), 'vm_sel_mode error'
        
        # select a VM
        print 'length of src__dict[src_idx] = ', len(src__dict[src_idx]), '\n\n'
        vm_obj_idx = src__dict[src_idx][0]
        del src__dict[src_idx][0]
        vm_obj = all_VM__dict[vm_obj_idx]
        
        vm_upSBW = vm_obj.upSBW
        vm_dnSBW = vm_obj.dnSBW
        vm_sigma = vm_obj.sigma
        
        # migrate to a DST
        if (dst_obj.upBW_tmp + vm_upSBW < dst_obj.BWC) & \
        (dst_obj.dnBW_tmp + vm_dnSBW < dst_obj.BWC) & \
        (dst_obj.sigma_tmp + vm_sigma < dst_obj.sigmaC):
            
            vm_obj.DSTnum = dst_idx
            
            # record the future service requirement in DST host    1)# dst_obj.upBW_tmp    2)# dst_obj.dnBW_tmp    3)# dst_obj.sigma_tmp
            dst_obj.upBW_tmp += vm_upSBW
            dst_obj.dnBW_tmp += vm_dnSBW
            dst_obj.sigma_tmp += vm_sigma                    
            
            # # #print_out every info in vm_obj
            # vm_obj.print_out()
            dst_obj.Final_upRBW -= vm_upSBW
            dst_obj.Final_dnRBW -= vm_dnSBW

            all_host__dict[vm_obj.SRCnum].Final_upRBW += vm_upSBW
            all_host__dict[vm_obj.SRCnum].Final_dnRBW += vm_dnSBW
            
            # # # mika debug...
            vm_obj.VM_god_migration(test_all_host__dict)
            
            src_obj.sigma_tmp -= vm_sigma
            migrated_vm__set.add(vm_obj_idx)
            
        else:
            assert(0), 'the fullest SRC cannot migr VM to the emptiest DST'
        
        # sort SRC/DST again
        src__list = sorted(src__list, key = lambda host_idx: all_host__dict[host_idx].sigma_tmp, reverse = True)
        dst__list = sorted(dst__list, key = lambda host_idx: all_host__dict[host_idx].sigma_tmp)
        
        target_src = all_host__dict[src__list[0]]
        target_dst = all_host__dict[dst__list[0]]
        
    # print 'all_VM__dict is ', all_VM__dict
    
    # delete unmigrated VMs in all_VM__dict
    copy_all_VM__set = set()
    for key, value in all_VM__dict.items():
        copy_all_VM__set.add(key)
    
    # print 'cp_VM__set is ', copy_all_VM__set
    
    to_be_del_vm__set = copy_all_VM__set - migrated_vm__set
    
    print 'migrated_vm__set is ', migrated_vm__set
    print 'to_be_del_vm__set', to_be_del_vm__set
    
    tmp__list = list(to_be_del_vm__set)
    for vm_idx in tmp__list:
        del all_VM__dict[vm_idx]
    
    # print 'all_VM__dict before rerification is ', all_VM__dict
    
    for key, vm_obj in all_VM__dict.items():
        if vm_obj.DSTnum == None: # 'There is a VM havnt alloc to DST since all the DSTs are full'
            return False



    # # # mika debug...
    for key, host_obj in test_all_host__dict.items():
        host_obj.assert_RBW()
        
    return True
    

    
def snapshot_gen(G, input_dict):
    ### tot_host_num can be 16 or 64
    ### src_num can be [4, 8, 12] in 16_mode
    ### migr_type can be 'Consolidation' or 'LoadBalancing'
    
    tot_host_num = input_dict['tot_host_num']
    src_num = input_dict['src_num']
    migr_type = input_dict['migr_type']
    
    
    all_host__dict = dict()
    all_VM__dict = dict()
    src__dict = dict()
    
    ### parameters about VM
    # vm_upSBW_range = (2, 8)
    # vm_dnSBW_range = (2, 8)
    # vm_sigma_range = (2, 8)
    # vm_ori_size_range = (30, 80) # GB
    vm_upSBW_range = input_dict [" vm_upSBW_range "]
    vm_dnSBW_range = input_dict [" vm_dnSBW_range "]
    vm_sigma_range = input_dict [" vm_sigma_range "]
    vm_ori_size_range = input_dict [" vm_ori_size_range "]
    
    
    
    
    
    ### parameters about host source limit
    if migr_type == 'Consolidation':
        # src_upBWC_range = (25, 30) # the unit is percentage
        # src_dnBWC_range = (25, 30)
        # src_sigmaC_range = (25, 30)
        # dst_upBWC_range = (70, 75)
        # dst_dnBWC_range = (70, 75)
        # dst_sigmaC_range = (70, 75)
        
        # src_upBWC_range = input_dict [" src_upBWC_range "] = (25, 30)
        # src_dnBWC_range = input_dict [" src_dnBWC_range "] = (25, 30)
        # src_sigmaC_range = input_dict [" src_sigmaC_range "] = (25, 30)
        # dst_upBWC_range = input_dict [" dst_upBWC_range "] = (70, 75)
        # dst_dnBWC_range = input_dict [" dst_dnBWC_range "] = (70, 75)
        # dst_sigmaC_range = input_dict [" dst_sigmaC_range "] = (70, 75)
        
        src_upBWC_range = input_dict [" src_upBWC_range "]
        src_dnBWC_range = input_dict [" src_dnBWC_range "]
        src_sigmaC_range = input_dict [" src_sigmaC_range "]
        dst_upBWC_range = input_dict [" dst_upBWC_range "]
        dst_dnBWC_range = input_dict [" dst_dnBWC_range "]
        dst_sigmaC_range = input_dict [" dst_sigmaC_range "]


    elif migr_type == 'LoadBalancing':
        # src_upBWC_range = (75, 95)
        # src_dnBWC_range = (75, 95)
        # src_sigmaC_range = (75, 95)
        # dst_upBWC_range = (30, 50)
        # dst_dnBWC_range = (30, 50)
        # dst_sigmaC_range = (30, 50)
        
        # src_upBWC_range = input_dict [" src_upBWC_range "] = (75, 95)
        # src_dnBWC_range = input_dict [" src_dnBWC_range "] = (75, 95)
        # src_sigmaC_range = input_dict [" src_sigmaC_range "] = (75, 95)
        # dst_upBWC_range = input_dict [" dst_upBWC_range "] = (30, 50)
        # dst_dnBWC_range = input_dict [" dst_dnBWC_range "] = (30, 50)
        # dst_sigmaC_range = input_dict [" dst_sigmaC_range "] = (30, 50)
        
        src_upBWC_range = input_dict [" src_upBWC_range "]
        src_dnBWC_range = input_dict [" src_dnBWC_range "]
        src_sigmaC_range = input_dict [" src_sigmaC_range "]
        dst_upBWC_range = input_dict [" dst_upBWC_range "]
        dst_dnBWC_range = input_dict [" dst_dnBWC_range "]
        dst_sigmaC_range = input_dict [" dst_sigmaC_range "]

    else:
        assert(0)
        
    vm_num_count = 0
    
    print 'snapshot_gen.py new SRC index 0~', (src_num -1)
    for i in range(tot_host_num):
        # print 'snapshot_gen.py new host_num', i
        if i < src_num: # SRC             
            # print 'snapshot_gen.py SRC generate'
            src__dict[i] = list()
            host_obj = Host_cl(G, 'SRC', i)
            
            src_upBWC = random.randint(src_upBWC_range[0], src_upBWC_range[1])
            src_dnBWC = random.randint(src_dnBWC_range[0], src_dnBWC_range[1])
            src_sigmaC = random.randint(src_sigmaC_range[0], src_sigmaC_range[1])
            # print 'snapshot_gen.py new SRC, src_num, upBW, dnBW, sigma', i, src_upBWC, src_dnBWC, src_sigmaC
            
            while 1:
                vm_upSBW = random.randint(vm_upSBW_range[0], vm_upSBW_range[1])
                vm_dnSBW = random.randint(vm_dnSBW_range[0], vm_dnSBW_range[1])
                vm_sigma = random.randint(vm_sigma_range[0], vm_sigma_range[1])
                vm_ori_size = random.randint(vm_ori_size_range[0], vm_ori_size_range[1])
                
                if (host_obj.upBW + vm_upSBW <= src_upBWC) &\
                (host_obj.dnBW + vm_dnSBW <= src_dnBWC) &\
                (host_obj.sigma + vm_sigma <= src_sigmaC):
                    # print 'snapshot_gen.py new VM into SRC, vm_upSBW, vm_dnSBW, vm_sigma, vm_ori_size', vm_upSBW, vm_dnSBW, vm_sigma, vm_ori_size
                    vm_obj = VM_cl2(G, vm_ori_size, vm_num_count, vm_upSBW, vm_dnSBW, vm_sigma, i)
                    host_obj.update(vm_upSBW, vm_dnSBW, vm_sigma, 'Consolidation')
                    
                    all_VM__dict[vm_num_count] = vm_obj
                    src__dict[i].append(vm_num_count)
                    

                    vm_num_count += 1 # equals to exact vm_number - 1
                else:
                    break
            # host_obj.print_out()

        else: # DST
            # print 'snapshot_gen.py SRC generate'
            host_obj = Host_cl(G, 'DST', i)
            
            dst_upBWC = random.randint(dst_upBWC_range[0], dst_upBWC_range[1])
            dst_dnBWC = random.randint(dst_dnBWC_range[0], dst_dnBWC_range[1])
            dst_sigmaC = random.randint(dst_sigmaC_range[0], dst_sigmaC_range[1])
            # print 'snapshot_gen.py new DST, dst_num, upBW, dnBW, sigma', dst_upBWC, dst_dnBWC, dst_sigmaC
            
            while 1:
                vm_upSBW = random.randint(vm_upSBW_range[0], vm_upSBW_range[1])
                vm_dnSBW = random.randint(vm_dnSBW_range[0], vm_dnSBW_range[1])
                vm_sigma = random.randint(vm_sigma_range[0], vm_sigma_range[1])
                vm_ori_size = random.randint(vm_ori_size_range[0], vm_ori_size_range[1])
                
                if (host_obj.upBW + vm_upSBW <= dst_upBWC) &\
                (host_obj.dnBW + vm_dnSBW <= dst_dnBWC) &\
                (host_obj.sigma + vm_sigma <= dst_sigmaC):
                    # print 'snapshot_gen.py new VM into DST, vm_upSBW, vm_dnSBW, vm_sigma, vm_ori_size', vm_upSBW, vm_dnSBW, vm_sigma, vm_ori_size
                    host_obj.update(vm_upSBW, vm_dnSBW, vm_sigma, 'Consolidation')
                else:
                    break
            # host_obj.print_out()
            
            
        all_host__dict[i] = host_obj
    
    
    print 'snapshot.py vm gen num', vm_num_count
    
    if migr_type == 'Consolidation':
        # result = True or False : indicating whether the snapshot is successfully generated or not
        result = migr_gen_C(G.VMmigr_gen_type, vm_num_count, src_num, all_host__dict, all_VM__dict, src__dict)
    elif migr_type == 'LoadBalancing': # LB case
        result = migr_gen_LB(G.input_dict['vm_sel_mode'], vm_sigma_range, src_num, all_host__dict, all_VM__dict, src__dict)
    else:
        assert(0)
    
    # print each vm element
    
    # # # make sure the migrations in the snapshot will never exceed the capacity constrain in SRCs and DSTs
    
    
    # for key, obj in all_host__dict.items():
        # obj.print_out()
    

    if len(all_VM__dict) <= 0 or len(all_host__dict) <= 0:
        result = False
    
    
    
    
    print'snapshot_gen: src__dict', src__dict
    return result, all_VM__dict, all_host__dict


