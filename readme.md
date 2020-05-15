# Semantic Property Task: annotation

This repository contains code to create input for an annotation task. In this task, property-concept pairs should be annotated with semantic relations. The property-concept pairs were collected from various resources (https://github.com/cltl/semantic_property_dataset).

The motivation of this data set is described in this paper:

@inproceedings{sommerauer-2020-why,
  title={Why is penguin more similar to polar bear than to sea gull? Analyzing conceptual knowledge in distributional models},
  author={Sommerauer, Pia},
  booktitle={Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop},
  year={in press}}

The collection of property-concept pairs to be annotated is outlined in this paper:

@inproceedings{sommerauer-etal-2019-towards,
	Address = {Wroclaw, Poland},
	Author = {Sommerauer, Pia and Fokkens, Antske and Vossen, Piek},
	Booktitle = {Proceedings of the 10th Global Wordnet Conference},
	Pages = {85--95},
	Title = {Towards Interpretable, Data-derived Distributional Semantic Representations for Reasoning: A Dataset of Properties and Concepts},
	Url = {https://clarin-pl.eu/dspace/handle/11321/718},
	Year = {2019},
	Bdsk-Url-1 = {https://clarin-pl.eu/dspace/handle/11321/718}}


Please use these references if you are using this repository in your research.

## Annotation task

The annotation task is set up as follows: Participants are presented with short descriptions of a relation between a property and a concept and asked to indicate whether they agree or disagree with the description.

Example of a single instance in the annotation task

![Task](images/task.png)

We run the task using the Lingoturk framework (https://github.com/FlorianPusse/Lingoturk) and distribute it via the platform Prolific (https://www.prolific.co/).

## Code

(1) Create all questions of a run of your experiment. Each question will receive a unique identifier. Do not change them anymore.

Each question consists of:

* property
* concept
* relation
* sentence describing the concept-property-relation
* a positive example of such a relation
* a negative example of such a relation
* pos and neg example property
* pos and neg example concept
* source of the property-concept pair

To create the questions, run:

`cd scripts/`
`python create_questions.py [run number]`

Replace `[run number]` with the experiment run. Currently, I created run3. The run number determines which descriptions of relations will be used (stored in `templates/`). The examples are taken from `examples/`.

(2) Create batches of questions which have not been annotated yet as you go.

`cd scripts/`
`python create_batch.py [prolific completion-url] [test/batch]`

Replace `[prolific completion-url]` with the completion url you received from Prolific when setting up the task on the platform. Replace `[test/batch]` with either 'test' (for testing) or 'batch' (for creating a batch).

(3) Launch the task:

* Upload your input to your Lingoturk platform
* Link the task to your Prolific Task
* Publish


The link to the annotated dataset will be made available here.


# Modification of examples or description templates

To modify examples, adapt the existing examples in `examples/[relation]-pairs.csv`.
When you're done, run:
`cd scripts`
`python add_properties_to_info.py`
Then add the information (property-category, etc) manually in the file `data/property_info.csv`
