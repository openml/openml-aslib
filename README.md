# OpenML-ASLib

Library that converts a set of experiments from OpenML into an ASLib scenario. The experiments are defined by either
* A study id
* A set of tasks and setup ids
* A benchmark suite and a set of scikit-learn classifiers

The remainder of this tutorial requires knowledge about basic OpenML components, such as datasets, tasks, flows and setups.
For an introduction to these concepts in the context of OpenML, please read this [blog post](https://medium.com/open-machine-learning/basic-components-of-openml-a5745634c664). 

## How to generate an ASLib scenario
There are several ways of using OpenML to generate new ASLib scenario's.

### Use an existing study
An OpenML study is a collection of datasets, tasks, flows, setups and runs.
Studies bundle these components in a single URL, convenient for attaching to a paper.
For example, [this study](https://www.openml.org/s/34) contains all algorithm runs that were used for the [OpenML-WEKA-2017 scenario](https://github.com/coseal/aslib_data/tree/master/OPENML-WEKA-2017). 

The OpenML-ASLib extension will take all registered tasks and setups from this study, and will try to find all corresponding runs on this cross-product on OpenML. 
Note that it is suggested to have the complete grid of algorithm performances (i.e., all setups should have been ran on all tasks).

Run example:
`python examples/generate_from_study.py --measure predictive_accuracy --study_id 34`
This generates a copy of the OpenML-WEKA-2017 scenario.

Alternatively, if the task ids and setup ids are already known (which requires some moderate OpenML skills) it is also possible to generate a scenario using these:
`python examples/generate.py -measure predictive_accuracy -task_ids 1701 1702 1705 -setup_ids 2361 2362`


### Generate runs on the fly

The example script `generate_from_sklearn.py` shows how to run several scikit-learn on an benchmark suite (= all tasks in an OpenML study) and create a ASLib scenario from this. 
In the [current example](https://github.com/openml/openml-aslib/blob/master/examples/generate_by_sklearn.py), a [Decision Stump](http://scikit-learn.org/stable/modules/tree.html) and [Naive Bayes](http://scikit-learn.org/stable/modules/naive_bayes.html) are ran on all tasks in the [OpenML-CC18](https://arxiv.org/abs/1708.03731), a curated benchmark suite. 
However, the script can be easily adapted to run on any benchmark suite or combination of scikit-learn classifiers. 
When the result of a given setup/task is already present on OpenML, the script will skip this combination and reuse the earlier result. 

