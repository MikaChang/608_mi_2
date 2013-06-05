# compute simulation result for this setting and iteration
def result_one_snap(G):
    print 'entering result_one_snapshot.py'
    
    output_dict = dict()
    output_dict['vm_migration_period__list'] = list()
    output_dict['sys_migration_period'] = None
    output_dict['accu_vm_migration_period'] = None
        
    min_migration_start_time = None
    max_migration_over_time = None

    
    tmp_start__list = list()
    tmp_over__list = list()
    tmp_migration_period__list = list()
    for vm_num, vm_obj in G.all_VM__dict.items():
        assert(vm_obj.status == 'completed')
        migration_start_time = vm_obj.migration_start_time
        migration_over_time = vm_obj.migration_over_time
        vm_migration_period = migration_over_time - migration_start_time

        tmp_start__list.append(migration_start_time)
        tmp_over__list.append(migration_over_time)
        tmp_migration_period__list.append(vm_migration_period)

    assert (len(tmp_start__list) > 0)
    assert (len(tmp_over__list) > 0)
    min_t = min(tmp_start__list)
    max_t = max(tmp_over__list)
    assert(min >=0)
    assert(max >=0)
    output_dict['sys_migration_period'] = max_t - min_t
    output_dict['accu_vm_migration_period'] = sum(tmp_migration_period__list)
    output_dict['accu_vm_deployment_time'] = sum(tmp_over__list)
    # output_dict['vm_migration_period__list'] = tmp_migration_period__list
    print '\n\nFinal result==='
    # print 'each vm migration period time', tmp_migration_period__list
    # print 'each vm migration start time', tmp_start__list
    # print 'each vm migration over time', tmp_over__list
    print 'output_dict', output_dict
    return output_dict
    