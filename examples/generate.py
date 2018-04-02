import argparse
import openml
import os

from openmlaslib.utils.scenario import generate_scenario

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
                                     description='Generates ASLib Scenario based on OpenML runs')
    parser.add_argument('--task_ids', type=int, nargs='+', required=True, help='openml task ids')
    parser.add_argument('--setup_ids', type=int, nargs='+', required=True, help='openml setup ids')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser('~').replace('\\', '/') + '/openml-aslib/')
    parser.add_argument('--measure', type=str, default='predictive_accuracy', help='measure that is being optimized')
    parser.add_argument('--require_complete', action='store_true', help='if set to true, an error is thrown if not all tasks are ran on all setups')
    args_ = parser.parse_args()

    generate_scenario(tasks=args_.task_ids,
                      setups=args_.setup_ids,
                      measure=args_.measure,
                      output_dir=args_.output_dir,
                      scenario_name='Misc',
                      require_complete=args_.require_complete)