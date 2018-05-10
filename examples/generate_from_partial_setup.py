import argparse
import collections
import json
import openml
import os
import openmlaslib


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Generates ASLib Scenario based on OpenML runs')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser('~').replace('\\', '/') + '/openml-aslib/')
    parser.add_argument('--study_id', default=123, type=int, help='openml study id')
    parser.add_argument('--measure', type=str, default='predictive_accuracy', help='measure that is being optimized')
    parser.add_argument('--require_complete', action='store_true', help='measure that is being optimized')
    parser.add_argument('--examplar_setups', type=json.loads, default='{"linear_svm": 7130285, "nonlinear_svm": 7130286}')
    args_ = parser.parse_args()

    # obtain study
    study = openml.study.get_study(args_.study_id, 'tasks')

    # bookkeeping
    given_setupname_setup = {name: openml.setups.get_setup(id) for name, id in args_.examplar_setups.items()}
    given_setupname_setupids = collections.defaultdict(list)

    # obtain all setups per category (given_setupname)
    for given_setupname, given_setup in given_setupname_setup.items():
        obtained_setupid_setup = openml.setups.list_setups(flow=given_setup.flow_id)
        for obtained_setupid, obtained_setup in obtained_setupid_setup.items():
            if openml.setups.is_partial_setup(given_setup, obtained_setup, ['random_state', 'categorical_features']):
                given_setupname_setupids[given_setupname].append(obtained_setupid)
        print('%s got %d setups' % (given_setupname, len(given_setupname_setupids[given_setupname])))

    # Generate the setupid_setupname dict
    setupid_setupname = dict()
    for name, setup_ids in given_setupname_setupids.items():
        for setup_id in setup_ids:
            setupid_setupname[setup_id] = name

    openmlaslib.utils.generate_scenario(tasks=study.tasks,
                                        setupid_setupname=setupid_setupname,
                                        measure=args_.measure,
                                        output_dir=args_.output_dir,
                                        scenario_name='Study_' + str(study.id),
                                        require_complete=args_.require_complete)
