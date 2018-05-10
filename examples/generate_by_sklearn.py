import argparse
import os
import openml
import openmlaslib
import sklearn.naive_bayes
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.tree


def cli_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Generates ASLib Scenario based on OpenML runs')
    parser.add_argument('--benchmark_suite', type=str, default='OpenML-CC18', help='the benchmark suite to run on')
    parser.add_argument('--output_dir', type=str, default=os.path.expanduser('~').replace('\\', '/') + '/openml-aslib/')
    parser.add_argument('--measure', type=str, default='predictive_accuracy', help='measure that is being optimized')
    parser.add_argument('--name', type=str, default='Misc', help='name of the scenario')
    return parser.parse_args()


def run_flow_on_benchmark_suite(estimator, task_ids):
    """
    Runs a flow on all tasks in an OpenML benchmark suite (for later use in OpenML ASLib)

    :param estimator: a model compatible with the sklearn API
    :param task_ids: a list of task ids
    :return: setup_id: the OpenML setup id of this model / hyperparameter combination
    """
    setup_id = None

    # set the random seed (important, as otherwise OpenML connector will choose one)
    if 'random_state' in estimator.get_params():
        estimator.set_params(random_state=1)
    # properly setup a pipeline (important to impute missing values)
    model = sklearn.pipeline.Pipeline(steps=[
        ('imputation', sklearn.preprocessing.Imputer(strategy='median')),
        ('estimator', estimator)
    ])

    # iterate over all tasks
    for task_id in task_ids:
        # download all task specific information (will be cached for later use)
        task = openml.tasks.get_task(task_id)
        print('Running %s on task %d (%s)' % (str(estimator), task_id, task.get_dataset().name))
        try:
            # run the model on the task
            run = openml.runs.run_model_on_task(task, model, avoid_duplicate_runs=True)
            # publish the run on OpenML
            run_id = run.publish().run_id
        except openml.exceptions.PyOpenMLError as e:
            # apparently someone already executed this run. No problem, we can re-use their results
            assert e.message.startswith('Run already exists in server.')
            run_ids = e.message.split('{')[1].split('}')[0].split(',')
            run_id = int(run_ids[0])
            print('- Already exists, using run id %d' % run_id)

        # obtain the stored run object from the server. This is how we will acquire the setup id
        # (which uniquely identifies this model / hyperparameter combination)
        run = openml.runs.get_run(run_id)
        if setup_id is None:
            setup_id = run.setup_id
        else:
            # sanity check
            if setup_id != run.setup_id:
                # if the setup id doesn't match, this means at least one of the hyperparameters
                # has changed across the tasks.
                # most likely candidates are the random seed or an indicator for categorical features,
                # if using a OneHotEncoder
                raise ValueError('Setup ids do not match')
    return setup_id


if __name__ == '__main__':
    args_ = cli_arguments()

    # download the benchmark suite (= a set of Machine Learning tasks) from OpenML
    benchmark_suite = openml.study.get_study(args_.benchmark_suite, 'tasks')

    # select the machine learning algorithms that we want to have in our ASLib Scenario.
    # In this case, Naive Bayes and a Decision Stump
    estimators = {
        'NaiveBayes': sklearn.naive_bayes.GaussianNB(),
        'DecisionStump': sklearn.tree.DecisionTreeClassifier(max_depth=1)
    }

    if openml.config.apikey is None:
        # set the OpenML API key. This can be done by creating a file called "config" in folder ~/.openml
        raise ValueError('Please set your OpenML API key (this is required when uploading results)')

    # a setup represents an algorithm with hyperparameter settings (sometimes called a configuration)
    # for more information about the OpenML nomocloture, read this blogpost:
    # https://medium.com/open-machine-learning/basic-components-of-openml-a5745634c664
    setupid_setupname = dict()
    
    # iterate over the machine learning algorithms
    for name, estimator in estimators.items():
        # the function `run_flow_on_benchmark_suite' will run the setup on all tasks
        setup_id = run_flow_on_benchmark_suite(estimator, benchmark_suite.tasks)
        # record the obtained setup id
        setupid_setupname[setup_id] = name

    # that's it. Now just create the benchmark suite ..
    openmlaslib.utils.generate_scenario(tasks=benchmark_suite.tasks,
                                        setupid_setupname=setupid_setupname,
                                        measure=args_.measure,
                                        output_dir=args_.output_dir,
                                        scenario_name=args_.name,
                                        require_complete=True)
