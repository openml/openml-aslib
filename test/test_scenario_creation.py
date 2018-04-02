import unittest
import openmlaslib
import os
import shutil

class TestMiscFunctions(unittest.TestCase):

    def setUp(self):
        self.default_dir = os.path.expanduser('~').replace('\\', '/') + '/openml-aslib-tests/'

    def tearDown(self):
        if os.path.isdir(self.default_dir):
            shutil.rmtree(self.default_dir)

    def test_create_scenario(self):
        openmlaslib.utils.generate_scenario(setups=[2361, 2362],
                                            tasks=[1701, 1702],
                                            measure='predictive_accuracy',
                                            output_dir=self.default_dir,
                                            scenario_name='test_create_scenario',
                                            require_complete=True)

    def test_create_imcomplete_setup_scenario(self):
        openmlaslib.utils.generate_scenario(setups=[2361, 2362, 0],
                                            tasks=[1701, 1702],
                                            measure='predictive_accuracy',
                                            output_dir=self.default_dir,
                                            scenario_name='test_create_imcomplete_setup_scenario',
                                            require_complete=False)

    def test_create_imcomplete_setup_scenario_raise(self):
        with self.assertRaises(Warning):
            openmlaslib.utils.generate_scenario(setups=[2361, 2362, 0],
                                                tasks=[1701, 1702],
                                                measure='predictive_accuracy',
                                                output_dir=self.default_dir,
                                                scenario_name='Misc',
                                                require_complete=True)

    def test_create_imcomplete_task_scenario(self):
        openmlaslib.utils.generate_scenario(setups=[2361, 2362],
                                            tasks=[1701, 1702, 0],
                                            measure='predictive_accuracy',
                                            output_dir=self.default_dir,
                                            scenario_name='test_create_imcomplete_task_scenario',
                                            require_complete=False)

    def test_create_imcomplete_task_scenario_raise(self):
        with self.assertRaises(Warning):
            openmlaslib.utils.generate_scenario(setups=[2361, 2362],
                                                tasks=[1701, 1702, 0],
                                                measure='predictive_accuracy',
                                                output_dir=self.default_dir,
                                                scenario_name='test_create_imcomplete_task_scenario_raise',
                                                require_complete=True)
