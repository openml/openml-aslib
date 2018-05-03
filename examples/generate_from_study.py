import argparse
import openml
import os
import openmlaslib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Generates ASLib Scenario based on OpenML runs')
    parser.add_argument('--study_id', required=True, type=int, help='openml study id')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser('~').replace('\\', '/') + '/openml-aslib/')
    parser.add_argument('--measure', type=str, default='predictive_accuracy', help='measure that is being optimized')
    parser.add_argument('--require_complete', action='store_true', help='measure that is being optimized')
    args_ = parser.parse_args()

    study = openml.study.get_study(args_.study_id)
    openmlaslib.utils.generate_scenario(tasks=study.tasks,
                                        setups=study.setups,
                                        measure=args_.measure,
                                        output_dir=args_.output_dir,
                                        scenario_name='Study_' + str(study.id),
                                        require_complete=args_.require_complete)
