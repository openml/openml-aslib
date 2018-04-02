# OpenML-ASLib

Library that converts a set of experiments from OpenML into an ASLib scenario. The experiments are defined by either
* A study id
* A set of tasks and setup ids

## Run

Run example:
`python examples/generate_from_study.py -measure 'predictive_accuracy' -study_id 34`

This will generate the scenario that corresponds with the following [study](https://www.openml.org/s/34). 