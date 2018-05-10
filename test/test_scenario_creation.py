import arff
import openmlaslib
import os
import shutil
import unittest
import yaml


class TestMiscFunctions(unittest.TestCase):

    def setUp(self):
        self.default_dir = os.path.expanduser('~').replace('\\', '/') + '/openml-aslib-tests/'

    def tearDown(self):
        if os.path.isdir(self.default_dir):
            shutil.rmtree(self.default_dir)

    @staticmethod
    def _setup_list_to_dict(setup_list):
        return {id: 'Setup_%d' % id for id in setup_list}

    def _test_generated_scenarios(self, directory, task_ids, setup_ids):
        num_runs = len(task_ids) * len(setup_ids)
        with open(os.path.join(directory, 'description.txt'), 'r') as fp:
            description = yaml.load(fp)
        self.assertEquals(set(description['algorithms_deterministic'].keys()),
                          set(TestMiscFunctions._setup_list_to_dict(setup_ids).values()))

        with open(os.path.join(directory, 'algorithm_runs.arff'), 'r') as fp:
            run_arff = arff.load(fp)
        self.assertEquals(len(run_arff['data']), num_runs)

        with open(os.path.join(directory, 'feature_runstatus.arff'), 'r') as fp:
            feature_status_aff = arff.load(fp)
        self.assertEquals(len(feature_status_aff['data']), len(task_ids))

        with open(os.path.join(directory, 'feature_values.arff'), 'r') as fp:
            feature_values_aff = arff.load(fp)
        self.assertEquals(len(feature_values_aff['data']), len(task_ids))

    def test_create_scenario(self):
        setups = [2361, 2362]
        tasks = [1701, 1702]
        scenario_name = 'test_create_scenario'
        openmlaslib.utils.generate_scenario(setupid_setupname=TestMiscFunctions._setup_list_to_dict(setups),
                                            tasks=tasks,
                                            measure='predictive_accuracy',
                                            output_dir=self.default_dir,
                                            scenario_name=scenario_name,
                                            require_complete=True)
        self._test_generated_scenarios(os.path.join(self.default_dir, scenario_name), tasks, setups)

    def test_create_imcomplete_scenario(self):
        # note that these setups can't be ran on both task (due to imputation parameter)
        setups = [6672945, 6777909]
        tasks = [3, 59]
        scenario_name = 'test_create_imcomplete_scenario'
        openmlaslib.utils.generate_scenario(setupid_setupname=TestMiscFunctions._setup_list_to_dict(setups),
                                            tasks=tasks,
                                            measure='predictive_accuracy',
                                            output_dir=self.default_dir,
                                            scenario_name=scenario_name,
                                            require_complete=False)
        self._test_generated_scenarios(os.path.join(self.default_dir, scenario_name), tasks, setups)

    def test_create_imcomplete_scenario_raise(self):
        # note that these setups can't be ran on both task (due to imputation parameter)
        with self.assertRaises(Warning):
            setups = [6672945, 6777909]
            tasks = [3, 59]
            scenario_name = 'test_create_imcomplete_scenario_raise'
            openmlaslib.utils.generate_scenario(setupid_setupname=TestMiscFunctions._setup_list_to_dict(setups),
                                                tasks=tasks,
                                                measure='predictive_accuracy',
                                                output_dir=self.default_dir,
                                                scenario_name=scenario_name,
                                                require_complete=True)
            self._test_generated_scenarios(os.path.join(self.default_dir, scenario_name), tasks, setups)

    def test_create_scenario_non_existing_setup(self):
        with self.assertRaises(Warning):
            setups = [2361, 2362, 0]
            tasks = [1701, 1702]
            scenario_name = 'test_create_scenario_non_existing_setup'
            openmlaslib.utils.generate_scenario(setupid_setupname=TestMiscFunctions._setup_list_to_dict(setups),
                                                tasks=tasks,
                                                measure='predictive_accuracy',
                                                output_dir=self.default_dir,
                                                scenario_name=scenario_name,
                                                require_complete=True)

    def test_create_scenario_non_existing_task(self):
        with self.assertRaises(Warning):
            setups = [2361, 2362]
            tasks = [1701, 1702, 0]
            scenario_name = 'test_create_scenario_non_existing_task'
            openmlaslib.utils.generate_scenario(setupid_setupname=TestMiscFunctions._setup_list_to_dict(setups),
                                                tasks=tasks,
                                                measure='predictive_accuracy',
                                                output_dir=self.default_dir,
                                                scenario_name=scenario_name,
                                                require_complete=True)
