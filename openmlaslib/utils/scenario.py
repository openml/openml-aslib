import arff
import yaml
import openml
import os


def generate_scenario(setups, tasks, measure, output_dir, scenario_name, require_complete=False):
    """ generates an ASlib scenario"""
    evaluations = openml.utils.list_all(openml.evaluations.list_evaluations,
                                        function=measure, setup=setups, task=tasks)
    total_dir = os.path.join(output_dir, scenario_name)
    try:
        os.makedirs(total_dir)
    except FileExistsError:
        pass

    setup_flowid = {}
    task_data_id = {}
    setup_scenarioname = {}
    task_setup_result = {}
    task_qualities = {}
    obtained_tasks = set()
    obtained_setups = set()

    # obtain the data and book keeping
    for run_id in evaluations.keys():
        task_id = evaluations[run_id].task_id
        flow_id = evaluations[run_id].flow_id
        data_id = evaluations[run_id].data_id
        setup_id = evaluations[run_id].setup_id
        value = evaluations[run_id].value

        task_data_id[task_id] = data_id
        setup_flowid[setup_id] = flow_id
        obtained_tasks.add(task_id)
        obtained_setups.add(setup_id)

        if task_id not in task_setup_result:
            task_setup_result[task_id] = {}
        task_setup_result[task_id][setup_id] = value

    if require_complete:
        if obtained_tasks != set(tasks):
            raise Warning('Tasks not found in evaluation list: %s' %(set(tasks) - obtained_tasks))
        if obtained_setups != set(setups):
            raise Warning('Setups not found in evaluation list: %s' %(set(setups) - obtained_setups))

    # obtain the meta-features
    complete_quality_set = None
    for task_id in obtained_tasks:
        qualities = openml.datasets.get_dataset(task_data_id[task_id]).qualities
        task_qualities[task_id] = qualities
        if complete_quality_set is None:
            complete_quality_set = qualities.keys()
        else:
            complete_quality_set = complete_quality_set & qualities.keys()
        print(task_id, qualities)
    complete_quality_set = list(complete_quality_set)
    print(complete_quality_set)

    algos = {}
    for setup_id in obtained_setups:
        flow = openml.flows.get_flow(setup_flowid[setup_id])
        name = '%s_%s' % (setup_id, flow.name)
        setup_scenarioname[setup_id] = name
        algos[name] = {'desterministic': True,
                       'version': flow.version,
                       'configuration': ''} # TODO

    description = {'scenario_id': 'OpenML_' + scenario_name,
                   'performance_measures': [measure],
                   'maximize': [True],
                   'performance_type': [measure],
                   'algorithm_cutoff_time': 0,
                   'algorithm_cutoff_memory': '?',
                   'features_cutoff_time': '?',
                   'features_cutoff_memory': '?',
                   'algorithms_deterministic': algos,
                   'algorithms_stochastic': '',
                   'features_deterministic': complete_quality_set,
                   'features_stochastic': '',
                   'number_of_feature_steps': 1,
                   'feature_steps': {'ALL': {'provides': complete_quality_set}},
                   'default_steps': ['ALL']}

    run_attributes = [['instance_id', 'STRING'],
                      ['repetition', 'NUMERIC'],
                      ['algorithm', 'STRING'],
                      [measure, 'NUMERIC'],
                      ['runstatus', ['ok', 'timeout', 'memout', 'not_applicable', 'crash', 'other']]
                     ]

    run_data = []
    for task_id in obtained_tasks:
        for setup_id in obtained_setups:
            if setup_id in task_setup_result[task_id]:
                perf = task_setup_result[task_id][setup_id]
                status = 'ok'
            elif require_complete:
                raise Warning('Not all setups were ran on all tasks. ' +
                              'Several missing, e.g., task %d setup %d' %(task_id, setup_id))
            else:
                perf = 0
                status = 'other'
            run_data.append([task_id, '1', setup_scenarioname[setup_id], perf, status])

    run_arff = {'attributes': run_attributes,
                'data': run_data,
                'relation': 'ALGORITHM_RUNS'
                }
    with open(os.path.join(total_dir, 'algorithm_runs.arff'), 'w') as fp:
        arff.dump(run_arff, fp)

    qualitystatus_attributes = [
        ['instance_id', 'STRING'],
        ['repetition', 'NUMERIC'],
        ['ALL', ['ok', 'timeout', 'memout', 'not_applicable', 'crash', 'other']]
    ]
    qualitystatus_data = []
    qualities_attributes = [['instance_id', 'STRING'],
                            ['repetition', 'NUMERIC']]
    for f in complete_quality_set:
        qualities_attributes.append([f, 'NUMERIC'])
    qualities_data = []
    for task_id in obtained_tasks:
        current_line = [task_id, '1']
        for idx, quality in enumerate(complete_quality_set):
            current_value = task_qualities[task_id][quality]
            current_line.append(current_value)
        qualities_data.append(current_line)
        qualitystatus_data.append([task_id, '1', 'ok'])

    qualities_arff = {'attributes': qualities_attributes,
                      'data': qualities_data,
                      'relation': 'FEATURES'
                     }
    with open(os.path.join(total_dir, 'feature_values.arff'), 'w') as fp:
        arff.dump(qualities_arff, fp)

    qualitystatus_arff = {'attributes': qualitystatus_attributes,
                          'data': qualitystatus_data,
                          'relation': 'FEATURES_RUNSTATUS'
                         }

    with open(os.path.join(total_dir, 'feature_runstatus.arff'), 'w') as fp:
        arff.dump(qualitystatus_arff, fp)

    with open(os.path.join(total_dir, 'description.txt'), 'w') as fp:
        yaml.dump(description, fp, default_flow_style=False)
