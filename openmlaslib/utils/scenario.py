import arff
import collections
import openml
import os
from typing import Dict, List, Set, Tuple
import yaml


def _obtained_data_to_run_arff(obtained_tasks: Set[int],
                               obtained_partialsetups: Set[str],
                               task_setup_result: Dict[int, Dict[str, float]],
                               measure: str, require_complete: bool):
    """
    Helper function that turns the obtained data into an dict for algorithm_runs.arff
    """
    run_attributes = [
        ['instance_id', 'STRING'],
        ['repetition', 'NUMERIC'],
        ['algorithm', 'STRING'],
        [measure, 'NUMERIC'],
        ['runstatus', ['ok', 'timeout', 'memout', 'not_applicable', 'crash', 'other']]
    ]

    run_data = []
    for task_id in obtained_tasks:
        completed_results_task = 0
        for setup_name in obtained_partialsetups:
            if setup_name in task_setup_result[task_id]:
                perf = task_setup_result[task_id][setup_name]
                status = 'ok'
                completed_results_task += 1
            elif require_complete:
                raise Warning('Not all setups were ran on all tasks. ' +
                              'Several missing, e.g., task %d setup %s' % (task_id, setup_name))
            else:
                perf = 0  # TODO: also allow for measures that are meant to be minimized
                status = 'other'
            run_data.append([task_id, '1', setup_name, perf, status])

        if completed_results_task == 0:
            raise ValueError('There were zero completed results on task %d, consider removing it ' % task_id)

    run_arff = {
        'attributes': run_attributes,
        'data': run_data,
        'relation': 'ALGORITHM_RUNS'
    }
    return run_arff


def generate_scenario(setupid_setupname: Dict[int, str], tasks: List[int], measure: str, output_dir: str,
                      scenario_name: str, require_complete: bool=False):
    """
    generates an ASlib scenario, and stores it to disk

    :param setupid_setupname: dict
        mapping from setup id to setup name. Multiple setup ids can map to the same setup name. In this case, these
        setup ids will be considered the same algorithm (for example, when algorithms are ran with a different random
        seed there will be various setup ids for a configuration that is practically the same)
    :param tasks: list
        contains all task ids involved
    :param measure: str
        the evaluation measure to be obtained from OpenML (e.g., predictive_accuracy, area_under_roc_curve)
    :param output_dir: str
        location where to save the files
    :param scenario_name: str
        the name to give to the scenario
    :param require_complete: bool
        if True, the script requires all estimators to be ran on all tasks (and throws an error if this condition is
        not met). Otherwise, an empty value (not finished) is recorded and run_status is set to other.
    """
    # make directory first (in case of failure)
    total_dir = os.path.join(output_dir, scenario_name)
    os.makedirs(total_dir, exist_ok=True)

    setupname_setupid = collections.defaultdict(list)
    for id, name in setupid_setupname.items():
        setupname_setupid[name].append(id)

    setup_flowid = {}
    task_data_id = {}
    task_setup_result = {}
    task_qualities = {}
    obtained_tasks = set()
    obtained_partialsetups = set()

    # obtain the data and book keeping
    evaluations = openml.evaluations.list_evaluations(function=measure, setup=setupid_setupname.keys(), task=tasks)
    for run_id in evaluations.keys():
        task_id = evaluations[run_id].task_id
        flow_id = evaluations[run_id].flow_id
        data_id = evaluations[run_id].data_id
        setup_id = evaluations[run_id].setup_id
        value = evaluations[run_id].value

        task_data_id[task_id] = data_id
        setup_flowid[setup_id] = flow_id
        obtained_tasks.add(task_id)
        obtained_partialsetups.add(setupid_setupname[setup_id])

        if task_id not in task_setup_result:
            task_setup_result[task_id] = {}
        task_setup_result[task_id][setupid_setupname[setup_id]] = value

    # this means there were zero results on this task. Throw error so user can throw it out.
    if obtained_tasks != set(tasks):
        raise Warning('Tasks not found in evaluation list: %s' % (set(tasks) - obtained_tasks))
    # this means there were zero results on this partialsetup. Throw error so user can throw it out.
    if obtained_partialsetups != set(setupid_setupname.values()):
        missing = set(setupid_setupname.values()) - obtained_partialsetups
        raise Warning('Setups not found in evaluation list: %s' % missing)

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

    algos = dict()
    for setup_name in obtained_partialsetups:
        setup_list = openml.setups.list_setups(setup=setupname_setupid[setup_name])
        if set(setup_list.keys()) != set(setupname_setupid[setup_name]):
            missing = set(setupname_setupid[setup_name]) - set(setup_list.keys())
            raise ValueError('Did not retrieve the following setups: %s' % missing)

        # check if all setups are from the same flow
        flow_id = list(setup_list.values())[0].flow_id
        for sid, setup in setup_list.items():
            if setup.flow_id != flow_id:
                raise ValueError('Not all setups are generated by same flow for %s' % setup_name)
        flow = openml.flows.get_flow(flow_id)

        algos[setup_name] = {'desterministic': True,
                             'version': flow.version,
                             'configuration': ''}  # TODO! use the hyperparameter dict from setup list

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

    run_arff = _obtained_data_to_run_arff(obtained_tasks,
                                          obtained_partialsetups,
                                          task_setup_result,
                                          measure,
                                          require_complete)
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
