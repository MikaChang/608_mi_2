import init_parameter
from init_parameter import SET__set, GP__set, SLOTTIME, ACCEPTABLE_MINI_VMM_DATA_RATE, RATE_PRECISION
from init_parameter import *
from init_update_func import *
from function import *
from concurrent_case import *
from randomCase import *
import math, copy


class Global_cl():
    def __init__(self, input_dict_):    
        self.E =  Event_list_cl(self)  # declare event_list, we store event_obj inside
        
        self.input_dict =dict()
        self.input_dict =copy.deepcopy(input_dict_)
        # ### smart input        
        
        # # self.migration_mode = 'StopNCopy'      # 'PreCopy' or 'StopNCopy'        
        # self.migration_mode = input_dict['migration_mode']      # 'PreCopy' or 'StopNCopy'
        
        # # self.algo_version = 'StrictSequence'
        # self.algo_version = input_dict['algo_version']
        
        # # self.VMmigr_gen_type = 'vmFirst'         #'vmFirst' or 'srcFirst'.
        # self.VMmigr_gen_type = input_dict['VMmigr_gen_type']         #'vmFirst' or 'srcFirst'.        
        # #**** vmFirst: largest VM search DST first.     
        # #**** srcFirst:  smallest SRC --> largest VM search DST first
        self.record_input_dict(self.input_dict)
        # ### smart input        
        
        
        self.now = 0            # record  'NOW' time    
        
        self.all_host__dict = dict()    # store all the host_obj   e.g.  all_host__dict[host_num] = host_obj
        self.all_VM__dict = dict()    # store all the VM_obj   e.g.  all_VM__dict[vm_num] = vm_obj
        
        self.SRC_host__set = set() # store all the SRC host_num  e.g. (host_num, host_num)
        self.DST_host__set = set()  # store all the DST host_num
        
        self.SetNum_to_VM__dict = dict()   # key: set number   value: vm_num set
        for i in SET__set:
            self.SetNum_to_VM__dict[i] = set()
                      
        self.SetNum_to_host__dict = dict()   # key: set number   value: host_num set
        for i in SET__set:
            self.SetNum_to_host__dict[i] = set()        
            
        self.GPNum_to_VM__dict = dict()  # key: group number   value: VM_num set
        for i in GP__set:
            self.GPNum_to_VM__dict[i] = set()
            
        self.GPNum_to_host__dict = dict()  # key: group number   value: host_num set
        for i in GP__set:
            self.GPNum_to_host__dict[i] = set()
            
        # ### Yen. for ran-scheduling algo. randomCase.py
        # ### tmp varible --> never use this kind of varible for decision making, only if you maintain varible value by yourself.        
        self.disjoint_VM__set = set()
        self.non_disjoint_VM__set = set()
        self.waiting_VM__set = set()            
            
    # # # update the decision making varible in G
    # # # just a bridge to connect G local varible and input dict.
    # # # after input are bridge into G, later coding style should let G to direct access input[].
    def record_input_dict(self, input_dict):
        self.VMmigr_gen_type = input_dict['VMmigr_gen_type']         #'vmFirst' or 'srcFirst'.        

        # # # algo related varible should update, if given from input_dict 
        # print 'record_input_dict() input_dict', input_dict
        for i in ["migration_mode", 'algo_version']:
            if i not in input_dict.keys():
                print 'record_input_dict() skip'
                return
        self.migration_mode = input_dict['migration_mode']      # 'PreCopy' or 'StopNCopy'
        self.algo_version = input_dict['algo_version']
        


        
    def refresh_G(self, input_dict_, all_host__dict, all_VM__dict):
        self.input_dict =copy.deepcopy(input_dict_)
        self.record_input_dict(self.input_dict)

    
        self.all_host__dict = copy.deepcopy(all_host__dict)    # store all the host_obj   e.g.  all_host__dict[host_num] = host_obj
        self.all_VM__dict = copy.deepcopy(all_VM__dict)
        for key, obj in self.all_host__dict.items():
            obj.G = self
        for key, obj in self.all_VM__dict.items():
            obj.G = self
            
            
            


class Event_list_cl():
    def __init__(self,G):
        self.list = []
        self.G = G
        self.event_num = 1
        
    def upcoming_event(self):
        # if len(list) == 0:
            # print 'Event_list_cl.upcoming_event() --> no further events'
            # return False, None           

        tmpL = sorted(self.list, key=lambda Event_cl: Event_cl.time)
        event_obj = tmpL.pop(0)
        self.list = tmpL
        if event_obj.time != self.G.all_VM__dict[event_obj.vm_num].last_migration_event_finish_time:
            # print 'now time:', self.G.now, 'Event_list_cl.upcoming_event --> skip event'
            # print 'Event_list_cl.upcoming_event() --> skip event'
            None
            return False, event_obj
        
        print 'Event_list_cl.upcoming_event()', 'event_num', event_obj.event_num
        return True, event_obj
        
    def insert_event_obj(self, event_obj):
        vm_num = event_obj.vm_num
        event_finish_time = event_obj.time
        event_obj.event_num = self.event_num
        # print 'now time:', self.G.now, 'Event_list_cl.insert_event_obj', 'vm_num', vm_num, 'event_finish_time', event_finish_time
        print 'Event_list_cl.insert_event_obj()', 'event_num', self.event_num, 'vm_num', vm_num, 'event_finish_time', event_finish_time
        self.list.append(event_obj)
        self.event_num += 1
        


class Host_cl():
    def __init__(self, G, type, host_num):
        self.G = G
        self.type = type   # type --> 'SRC' or 'DST'
        
        
        ### Louis used in snapshot_gen.py. Only meaningful in snapshot_gen()
        ### tmp varible --> never use this kind of varible for decision making, only if you maintain varible value by yourself.        
        self.size = 100.0
        self.BWC = 100.0
        self.upBW = 0.0
        self.dnBW = 0.0
        self.sigmaC = 100.0
        self.sigma = 0.0
        
        # # # tmp varible....for use in snapshot_gen.py 
        # ## tmp varible --> never use this kind of varible for decision making, only if you set varible value by yourself.
        # # #
        self.upBW_tmp = 0.0
        self.dnBW_tmp = 0.0        
        self.sigma_tmp = 0.0                
        ### Louis
        
        
        self.host_num = host_num        
        self.upRBW = 0.0   # now residual up BW
        self.dnRBW = 0.0   # now residual down BW
        self.Initial_upRBW = 0.0   # For get_set_num use:   residual up BW exclusive of the migration data rate. 
        self.Initial_dnRBW = 0.0   # 
        self.Final_upRBW = 0.0   # Final residual up BW after all VMM complete
        self.Final_dnRBW = 0.0   # Final residual down BW after all VMM complete
        
        ### tmp varible --> never use this kind of varible for decision making, only if you maintain varible value by yourself.
        self.upRBW_tmp = 0.0   # now residual up BW
        self.dnRBW_tmp = 0.0   # now residual down BW        
        
        # self.all_VM__dict = dict()  #dict to record VM inside the host
        
        self.waiting_vm__set = set()  # set() to record the  vm_num (waiting migration)
        self.sending_vm__set = set()  # set() to record the  vm_num (sending migration)
        
        self.reg_q__Set = set()   # set() to record the vm_num waiting for migrations with registration
        
        self.GPNum_to_VM__dict = dict()
        for i in GP__set:
            self.GPNum_to_VM__dict[i] = set()   ### key: group number   value: VM_obj set
                                                                                                            ###^^^^^^^^^^^

    ### Louis: take care of final_RBW in LB case!!!
    def update(self, vm_upSBW, vm_dnSBW, vm_sigma, migr_type):
        self.upBW += vm_upSBW
        self.dnBW += vm_dnSBW
        self.sigma += vm_sigma
        
        # # # build varibles in snapshot_gen.py migr_gen_C()
        self.upBW_tmp += vm_upSBW
        self.dnBW_tmp += vm_dnSBW
        self.sigma_tmp += vm_sigma
                
        self.upRBW = self.BWC - self.upBW
        self.dnRBW = self.BWC - self.dnBW
        self.Initial_upRBW = self.BWC - self.upBW
        self.Initial_dnRBW = self.BWC - self.dnBW
        self.Final_upRBW = self.BWC - self.upBW
        self.Final_dnRBW = self.BWC - self.dnBW
        
        # ### I don't know what it means.....
        # if migr_type == 'LoadBalancing':
            # self.Final_upRBW = self.BWC - self.upBW
            # self.Final_dnRBW = self.BWC - self.dnBW
        # else:
            # assert(0)
            
            
    def assert_RBW(self):
        assert(self.upRBW >= 0 and self.upRBW <= self.BWC + RATE_PRECISION), '%.20f, %.20f' % (self.upRBW, self.BWC)
        assert(self.dnRBW >= 0 and self.dnRBW <= self.BWC + RATE_PRECISION), '%.20f, %.20f' % (self.dnRBW, self.BWC)
            

    def print_out(self):
        print 'host_obj.print_out(): num', self.host_num, 'upRBW', self.upRBW, 'dnRBW', self.dnRBW, 'self.Initial_upRBW', self.Initial_upRBW,'self.Initial_dnRBW', self.Initial_dnRBW, 'self.Final_upRBW', self.Final_upRBW, 'self.Final_dnRBW', self.Final_dnRBW
        
class VM_cl2():
    def __init__(self, G, ori_size, vm_num, upSBW, dnSBW, sigma, SRCnum):
        self.G = G
        self.ori_size = float(ori_size) # original size of VM
        
        ### Louis
        self.sigma = float(sigma) 
        ### Louis
        
        self.remain_size = float(ori_size)  # after some time period, the remaining size for migration
        self.upSBW = float(upSBW)  #vm uplink service BW
        self.dnSBW = float(dnSBW)  #vm downlink service BW

        self.upBSratio = float(upSBW) / ori_size
        self.upSBratio = ori_size / float(upSBW)
        self.dnBSratio = float(dnSBW) / ori_size
        self.dnSBratio = ori_size/(float(dnSBW))
        
        self.latest_data_rate = 0.0
        self.tmp_rate = 0.0       # tmp rate --> for coding efficiency. no actually power
        
        # self.host_num = host_num  #vm belong to # host (now position)
        self.vm_num = vm_num  #vm number
        
        self.SRCnum = SRCnum  #the host SRC number
        self.DSTnum = None  #the host DST number
        self.status = "waiting"     # status ==> 'waiting', 'sending', 'completed'
        # self.dominant = "Null"   # dominant host = 'SRC' or 'DST'    ###useless
        # self.set_type = 'Null'   # 1 or 2 or 3  ==> use number not string!!!!!
        self.set_num = None  # value = 1,2,3
        
        self.migration_start_time = 0
        self.migration_over_time = 0
        self.last_migration_event_finish_time = 0  # 1) let event queue check whether the event from event queue is the latest or the expired event. 2) let node update his migration progress upon event. VM can compute the period during two time checkpoint, thus the migration progress can be computed
        self.last_migration_event_schedule_time = 0  #record the event schedule time
        

        
    def print_out(self):
        print 'vm_obj.print_out(): num', self.vm_num, 'SRC', self.SRCnum, 'DST', self.DSTnum, 'upSBW', self.upSBW, 'dnSBW', self.dnSBW, 'size', self.ori_size, 'upSBratio', self.upSBratio, 'dnSBratio', self.dnSBratio
        
        
    def next_status(self):
        if self.status == 'waiting':
            self.status = 'sending'
        elif self.status == 'sending':
            self.status = 'completed'
        else:
            assert(0)
        
    def get_set_num(self):     # return the set number for each VMM, e.g. 1 2 3   <== int. only
        assert (self.status == 'waiting')
        SRChost = self.G.all_host__dict[self.SRCnum]
        DSThost = self.G.all_host__dict[self.DSTnum]
        
        SRC_now = copy.copy(SRChost.Initial_upRBW)
        if self.G.migration_mode == 'StopNCopy':
            SRC_now += self.upSBW
        else:
            assert (self.G.migration_mode == 'PreCopy')
        SRC_end = SRChost.Final_upRBW
        DST_now = DSThost.Initial_dnRBW
        DST_end = DSThost.Final_dnRBW
        
        # assert(SRC_now < SRC_end and DST_now < DST_end), \
        # 'src_now %.20f src_end %.20f dst_now %.20f dst_end %.20f' % (SRC_now, SRC_end, DST_now, DST_end)
        
        if SRC_now >= DST_now and SRC_end >= DST_end:
            self.set_num = 1
        elif SRC_now < DST_now and SRC_end >= DST_end:
            self.set_num = 2
        elif SRC_now < DST_now and SRC_end < DST_end:
            self.set_num = 3
        else:
            assert(0)
        
        return self.set_num

            

### for all parallel algo. --> vm rate may change during migraton proceedings
    def adjust_VM_BW(self, rate):  
        assert (rate > 0), rate
        print 'basic.py:  vm_obj.adjust_VM_BW  rate=',rate, '  vm_num', self.vm_num
        # update  vm_obj.remain_size according latest_data_rate 
        last_round_migration_period = self.G.now - self.last_migration_event_schedule_time
        self.remain_size -= float(last_round_migration_period) * self.latest_data_rate

    
        assert(self.status == 'sending')
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        
        #release old data rate for SRC and DST
        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW
        SRCobj.upRBW += self.latest_data_rate
        DSTobj.dnRBW += self.latest_data_rate
        SRCobj.upRBW -= rate
        DSTobj.dnRBW -= rate

        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW
        self.latest_data_rate = rate
                
        ### schedule Event_cl() into event list
        finish_time = self.compute_finish_time()
        tmp_info__dict = dict()
        tmp_type = 'vm_finish'
        event_obj = Event_cl(self.G, tmp_type, finish_time, self.vm_num, tmp_info__dict)
        
        assert (self.migration_start_time != 0)        
        self.G.E.insert_event_obj(event_obj)

        # # # make sure src and dst RBW are reasonable
        self.assert_host_RBW()

        
        
        
    def concurrent_resetVM_BW(self):  
        # update  vm_obj.remain_size according latest_data_rate 
    
        assert(self.status == 'sending')
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        
        #release old data rate for SRC and DST
        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW
        SRCobj.upRBW += self.latest_data_rate
        DSTobj.dnRBW += self.latest_data_rate

    def concurrent_adjust_VM_BW(self, rate):  
        # update  vm_obj.remain_size according latest_data_rate 
        last_round_migration_period = self.G.now - self.last_migration_event_schedule_time
        self.remain_size -= float(last_round_migration_period) * self.latest_data_rate
    
        assert(self.status == 'sending')
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        
        #release old data rate for SRC and DST
        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW
        SRCobj.upRBW -= rate
        DSTobj.dnRBW -= rate

        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), '%.50f, %.50f, %d' %(DSTobj.dnRBW,rate,self.vm_num)
        self.latest_data_rate = rate
                
        ### schedule Event_cl() into event list
        finish_time = self.compute_finish_time()
        tmp_info__dict = dict()
        tmp_type = 'vm_finish'
        event_obj = Event_cl(self.G, tmp_type, finish_time, self.vm_num, tmp_info__dict)
        
        # assert (self.migration_start_time != 0)        
        assert (self.migration_start_time <= self.G.now)        
        self.G.E.insert_event_obj(event_obj)

        # # # make sure src and dst RBW are reasonable
        self.assert_host_RBW()        
        

    def release_BW(self):   # release the BW usage.   SRC release uplink, DST release dnlink
        print 'basic.py:  vm_obj.release_BW', 'vm_num', self.vm_num, 'status changing from=',self.status
        assert (self.status == 'sending')
        
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        
        # # #  release the BW used by migration process
        SRCobj.upRBW += self.latest_data_rate
        DSTobj.dnRBW += self.latest_data_rate
        
        # # #before activation VM at DST, try to make sure that RBW is enough for activation
        up_BWshortage = DSTobj.upRBW - self.upSBW
        dn_BWshortage = DSTobj.dnRBW - self.dnSBW
        ongoing_SRC_VM_rate_adjust = False
        if (up_BWshortage < 0 or dn_BWshortage < 0):
            None
            # assert(0), 'up_BWshortage: %f  dn_BWshortage: %f ' % (up_BWshortage, dn_BWshortage)
            assert (up_BWshortage >=0), 'up_BWshortage %f' % (up_BWshortage)
            debet_dnBW = abs(dn_BWshortage)
            
            vm_num_list = sorted(list(DSTobj.sending_vm__set), key = lambda vm_num: self.G.all_VM__dict[vm_num].latest_data_rate, reverse = True)
            for i in vm_num_list:
                if i == self.vm_num:
                    continue
                vm_obj = self.G.all_VM__dict[i]
                now_rate = vm_obj.latest_data_rate
                if now_rate > debet_dnBW:
                    new_rate = now_rate - debet_dnBW
                    vm_obj.adjust_VM_BW(new_rate)
                    ongoing_SRC_VM_rate_adjust = True
                    SRCobj = self.G.all_host__dict[vm_obj.SRCnum]
                    vm_raised = i
                    break
            assert(ongoing_SRC_VM_rate_adjust == True)
        # # # VM activation at DST:  vm service BW will decrease DST upRBW and dnRBW
        DSTobj.upRBW -= self.upSBW
        DSTobj.dnRBW -= self.dnSBW
        DSTobj.Initial_upRBW -= self.upSBW
        DSTobj.Initial_dnRBW -= self.dnSBW
        
        # # # release the BW used by vm service at src
        if self.G.migration_mode == 'PreCopy':
            SRCobj.upRBW += self.upSBW    # PreCopy mode!!!
            SRCobj.dnRBW += self.dnSBW    # PreCopy mode!!!
            SRCobj.Initial_upRBW += self.upSBW    # StopNCopy mode!!!
            SRCobj.Initial_dnRBW += self.dnSBW    # StopNCopy mode!!!
        else:
            assert (self.G.migration_mode == 'StopNCopy')
            
        assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW
        
        SRCobj.sending_vm__set -= set([self.vm_num])
        DSTobj.sending_vm__set -= set([self.vm_num])        
        ###update vm_obj.status
        self.next_status()

        self.migration_over_time = self.G.now

        # # #  adjust ongoing VM rate at SRC
        if ongoing_SRC_VM_rate_adjust == True:
            # SRCobj_tmp = G.all_host__dict[G.all_VM__dict[vm_raised].SRCnum].sending_vm__set
            for vm_num in self.G.all_host__dict[self.G.all_VM__dict[vm_raised].SRCnum].sending_vm__set:
                vm_obj = self.G.all_VM__dict[vm_num]
                old_rate = vm_obj.latest_data_rate
                result, dataRate = vm_obj.speed_checking('partial',None)
                if result == 'success' and dataRate > vm_obj.latest_data_rate:
                    vm_obj.adjust_VM_BW(dataRate)
                
                
        

        # # # make sure src and dst RBW are reasonable
        self.assert_host_RBW()

    
    def migration_over(self):
        # print 'basic.py  vm_obj.migration_over() vm_num=', self.vm_num
        if self.status != 'sending':
            print 'basic.py  vm_obj.migration_over() skip vm_num=', self.vm_num
            # # # identical event are scheduled into event_list. No program logic error, don't worry !!!
            # # #  this assert should disable, because identical event with the same event time in event_list  may be recorded.
            # # # it is inevitable
            # assert(0), self.status            
            if self.status == 'waiting':
                assert(0)
            return
        else:
            print 'basic.py  vm_obj.migration_over() vm_num=', self.vm_num
        if self.G.algo_version != 'ConCurrent':
            # # # ConCurrent algo maintain the resource by themself
            self.release_BW()
        
        if self.G.algo_version == 'StrictSequence':
            func_SS_update_ongoing(self.G,self.vm_num)
            ### can change to multiple SS G functions
            func_SS_modified(self.G)
            # func_SS(self.G, 1, 'descending', self.vm_num)
            # func_SS(self.G, 2, 'descending', self.vm_num)
        elif self.G.algo_version == 'ConCurrent':
            func_Concurrent_Ongoing(self.G,self.vm_num)
        elif self.G.algo_version == 'RanSequence':
            func_ran_disjoint_ongoing(self.G, self.vm_num)
        
        
    def assign_VM_BW(self, rate):       
        print 'basic.py:  vm_obj.assign_VM_BW  rate=',rate, '  vm_num', self.vm_num
        assert(rate > 0), rate
        assert(self.status == 'waiting')
    
        ### assign VM BW into SRC, DST
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        if self.G.migration_mode == 'StopNCopy':
            SRCobj.upRBW += self.upSBW    # StopNCopy mode!!!
            SRCobj.dnRBW += self.dnSBW    # StopNCopy mode!!!
            SRCobj.Initial_upRBW += self.upSBW    # StopNCopy mode!!!
            SRCobj.Initial_dnRBW += self.dnSBW    # StopNCopy mode!!!
        else:
            assert (self.G.migration_mode == 'PreCopy')
            
        # # #vm activation, update the RBW at src and dst
        SRCobj.upRBW -= rate
        DSTobj.dnRBW -= rate
        # assert(SRCobj.upRBW >= 0), SRCobj.upRBW
        # assert(DSTobj.dnRBW >= 0), DSTobj.dnRBW        
        
        # # # update the vm related status store in SRCobj and DSTobj
        self.next_status()
        self.latest_data_rate = rate
        SRCobj.waiting_vm__set -= set([self.vm_num])
        DSTobj.waiting_vm__set -= set([self.vm_num])
        SRCobj.sending_vm__set.add(self.vm_num)
        DSTobj.sending_vm__set.add(self.vm_num)
        
        ### schedule Event_cl() into event list
        finish_time = self.compute_finish_time()
        tmp_info__dict = dict()
        tmp_type = 'vm_finish'
        event_obj = Event_cl(self.G, tmp_type, finish_time, self.vm_num, tmp_info__dict)
        
        self.G.E.insert_event_obj(event_obj)

        # # # delete the willing to wait on other side host 
        SRCobj.reg_q__Set.discard(self.vm_num)
        DSTobj.reg_q__Set.discard(self.vm_num)
        for i in GP__set:
            SRCobj.GPNum_to_VM__dict[i].discard(self)   # key: group number   value: VM_obj set
            DSTobj.GPNum_to_VM__dict[i].discard(self)   # key: group number   value: VM_obj set
            
        # # # make sure src and dst RBW are reasonable
        self.assert_host_RBW()
        
        
    def compute_finish_time(self):
        time = self.remain_size / float(self.latest_data_rate)
        # assert (self.latest_data_rate > 0), self.latest_data_rate
        # assert (self.remain_size >0), '%.50f' % (self.remain_size)
        # assert(time > 0), time
        finish_time = int(math.floor(time / SLOTTIME))
        # finish_time = time / SLOTTIME
        assert (finish_time >=0), finish_time
        finish_time *= SLOTTIME
        finish_time += self.G.now 
        return finish_time
        
    # ###########
    # speed_checking() will try to check whether the SRC and DST have any BW for the VM.
    # the return value includes:   flag, miniRate.
    # flag = True ==> SRC and DST both have BW for VM
    # miniRate ==> indicate the min residual BW between SRC and DST    
    def speed_checking(self, BW_mode, domi_node):    # e.g. BW_mode = 'full', 'partial'   domi_node = 'SRC', 'DST'
        # print 'now time:', self.G.now
        print 'basic.py:  vm_obj.speed_checking()',  'vm_num=', self.vm_num,'BW_mode=',BW_mode, '  domi_node', domi_node
        
        ###########################

        ###
        # on-going vm --> just return fail
        if self.status == 'completed':
            assert(0)
            # return 'fail', None
        
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        upRate = copy.copy(SRCobj.upRBW)
        dnRate = copy.copy(DSTobj.dnRBW)
        print 'basic.py speed_checking()_1:  upRate, dnRate', upRate, dnRate
        
        if self.status == 'sending':
            upRate += self.latest_data_rate
            dnRate += self.latest_data_rate
        elif self.G.migration_mode == 'StopNCopy' and self.status == 'waiting':
            upRate += self.upSBW   # StopNCopy mode!!!
        print 'basic.py speed_checking()_2:  upRate, dnRate', upRate, dnRate

        minRate = min(upRate, dnRate)
        if minRate == upRate:
            None
            # print 'basic.py:  vm_obj.speed_checking() minRate from SRC.upRate'
        elif minRate == dnRate:
            None
            # print 'basic.py:  vm_obj.speed_checking() minRate from DST.dnRate'

        Rate_tmp = minRate / float(RATE_PRECISION)        
        Rate_tmp = int(Rate_tmp) * RATE_PRECISION
        minRate = Rate_tmp

        if minRate == 0 or minRate <= ACCEPTABLE_MINI_VMM_DATA_RATE:
            minRate = 0.0
            mode_result = 'fail'
            # print 'basic.py:  vm_obj.speed_checking()  return fail    miniRate=', 0
            # return 'fail', 0
        else:
            mode_result = 'success'
            if BW_mode == 'partial':
                assert(domi_node == None)
            elif BW_mode == 'full':
                if domi_node =='DST':
                    None
                    # assert (abs(minRate - dnRate) <= RATE_PRECISION), (minRate, dnRate)
                    if self.G.input_dict['SS_level']  == 'full' and len(DSTobj.sending_vm__set) != 0:
                        mode_result = 'fail'
                        # assert(0)
                        
                elif domi_node =='SRC':
                    None
                    # assert (abs(minRate - upRate) <= RATE_PRECISION), (minRate, upRate)
                    if self.G.input_dict['SS_level']  == 'full' and len(SRCobj.sending_vm__set) != 0:
                        mode_result = 'fail'
                        # assert(0)
                    
                else:
                    assert(0)
            else:
                assert(0)
            
        print 'basic.py:  vm_obj.speed_checking()  return     result', mode_result, 'minRate', minRate
        return mode_result, minRate    
        ###

        
    # # # check for the src and dst RBW. Make sure both RBW ==>   0<RBW<host_obj.BWC
    def assert_host_RBW(self):
        SRCobj = self.G.all_host__dict[self.SRCnum]
        DSTobj = self.G.all_host__dict[self.DSTnum]
        print 'basic.py assert_host_RBW() vm_num=', self.vm_num
        
        assert(SRCobj.upRBW >= - RATE_PRECISION  and SRCobj.upRBW <= SRCobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (SRCobj.upRBW, SRCobj.BWC)
        assert(DSTobj.upRBW >= - RATE_PRECISION  and DSTobj.upRBW <= DSTobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (DSTobj.upRBW, DSTobj.BWC)
        assert(SRCobj.dnRBW >= - RATE_PRECISION  and SRCobj.dnRBW <= SRCobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (SRCobj.dnRBW, SRCobj.BWC)
        assert(DSTobj.dnRBW >= - RATE_PRECISION  and DSTobj.dnRBW <= DSTobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (DSTobj.dnRBW, DSTobj.BWC)
        
        assert(SRCobj.Initial_upRBW >= - RATE_PRECISION  and SRCobj.Initial_upRBW <= SRCobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (SRCobj.Initial_upRBW, SRCobj.BWC)
        assert(DSTobj.Initial_upRBW >= - RATE_PRECISION  and DSTobj.Initial_upRBW <= DSTobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (DSTobj.Initial_upRBW, DSTobj.BWC)
        assert(SRCobj.Initial_dnRBW >= - RATE_PRECISION  and SRCobj.Initial_dnRBW <= SRCobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (SRCobj.Initial_dnRBW, SRCobj.BWC)
        assert(DSTobj.Initial_dnRBW >= - RATE_PRECISION  and DSTobj.Initial_dnRBW <= DSTobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (DSTobj.Initial_dnRBW, DSTobj.BWC)
        
        assert(SRCobj.Final_upRBW >= - RATE_PRECISION  and SRCobj.Final_upRBW <= SRCobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (SRCobj.Final_upRBW, SRCobj.BWC)
        assert(DSTobj.Final_upRBW >= - RATE_PRECISION  and DSTobj.Final_upRBW <= DSTobj.BWC + RATE_PRECISION), '%.20f, %.20f' % (DSTobj.Final_upRBW, DSTobj.BWC)
        assert(SRCobj.Final_dnRBW >= - RATE_PRECISION  and SRCobj.Final_dnRBW <= SRCobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (SRCobj.Final_dnRBW, SRCobj.BWC)
        assert(DSTobj.Final_dnRBW >= - RATE_PRECISION  and DSTobj.Final_dnRBW <= DSTobj.BWC+ RATE_PRECISION), '%.20f, %.20f' % (DSTobj.Final_dnRBW, DSTobj.BWC)
        
        
        
        RATE_PRECISION_2 = 0.5
        # assert(SRCobj.upRBW >= 0 and SRCobj.upRBW <= SRCobj.BWC + RATE_PRECISION_2), '%.20f, %.20f' % (SRCobj.upRBW, SRCobj.BWC)
        # assert(DSTobj.upRBW >= 0 and DSTobj.upRBW <= DSTobj.BWC + RATE_PRECISION_2), '%.20f, %.20f' % (DSTobj.upRBW, DSTobj.BWC)

        # assert(SRCobj.dnRBW >= 0 and SRCobj.dnRBW <= SRCobj.BWC+ RATE_PRECISION_2), '%.20f, %.20f' % (SRCobj.dnRBW, SRCobj.BWC)
        # assert(DSTobj.dnRBW >= 0 and DSTobj.dnRBW <= DSTobj.BWC+ RATE_PRECISION_2), '%.20f, %.20f' % (DSTobj.dnRBW, DSTobj.BWC)        
       
       

    # # # Super migration ==> instantly migrate VM from SRC to DST without any cost. this function deal with SRC/DST/upRBW/dnRBW varible.
    # # # for confirmation in snapshot_gen.py to make sure the VM migration will never violate the capacity constrain at SRCs and DSTs
    def VM_god_migration(self, all_host__dict = None):
        assert(all_host__dict != None) 
        if all_host__dict == None:
            all_host__dict = self.G.all_host__dict
        
        # SRCupR = all_host__dict[self.SRCnum].upRBW
        # SRCdnR = all_host__dict[self.SRCnum].dnRBW
        # DSTupR = all_host__dict[self.DSTnum].upRBW
        # DSTdnR = all_host__dict[self.DSTnum].dnRBW
        
        # VMup = self.upSBW
        # VMdn = self.dnSBW

        # # release SBW at SRC
        # SRCupR += VMup
        # SRCdnR += VMdn
        
        # # occupy SBW at DST
        # DSTupR -= VMup
        # DSTdnR -= VMdn        
        

        # SRCupR = all_host__dict[self.SRCnum].upRBW
        # SRCdnR = all_host__dict[self.SRCnum].dnRBW
        # DSTupR = all_host__dict[self.DSTnum].upRBW
        # DSTdnR = all_host__dict[self.DSTnum].dnRBW
        
        # VMup = self.upSBW
        # VMdn = self.dnSBW

        # release SBW at SRC
        all_host__dict[self.SRCnum].upRBW += self.upSBW
        all_host__dict[self.SRCnum].dnRBW += self.dnSBW
        
        # occupy SBW at DST
        all_host__dict[self.DSTnum].upRBW -= self.upSBW
        all_host__dict[self.DSTnum].dnRBW -= self.dnSBW                
        
        
        
        
        
        
        
class Event_cl():
    def __init__(self, G, type, time, vm_num, info__dict = dict()):
        assert(time > 0)
        self.G = G
        self.type = type
        self.time = time        #event finish time
        self.event_schedule_time = G.now        #time: schedule the event
        self.vm_num = vm_num
        self.info__dict = copy.deepcopy(info__dict)
        self.event_num = 0
        
        self.write_time_to_vm_obj()
        
    def write_time_to_vm_obj(self):
        vm_obj = self.G.all_VM__dict[self.vm_num]
        assert(self.time >= self.G.now)
        assert(vm_obj.last_migration_event_schedule_time <= self.G.now)
        vm_obj.last_migration_event_finish_time = self.time
        vm_obj.last_migration_event_schedule_time = self.G.now
        if vm_obj.migration_start_time == 0:
            vm_obj.migration_start_time = self.G.now        
        
