from utils import read_csv, to_csv
from utils import sort_by_key
from utils import read_group

from random import shuffle, choice
import os
import sys

def read_input(run, experiment_name):
    all_input_dicts = []
    dir_path = f'../prolific_input/run{run}-group_{experiment_name}/'
    header_path = f'{dir_path}header.txt'
    batch_numbers = []

    with open(header_path) as infile:
        header = infile.read().split(',')

    filepaths = os.listdir(dir_path)
    for f in filepaths:
        full_path = f'{dir_path}{f}'
        input_dicts = read_csv(full_path, header = header)
        all_input_dicts.extend(input_dicts)
        # # qu70-s_qu70-batch18.csv
        if f != 'header.txt':
            batch_n = int(f.split('-')[2].split('.')[0][len('batch'):])
            batch_numbers.append(batch_n)
    return all_input_dicts, batch_numbers

def collect_not_annotated(input_dicts, question_dicts):

    questions_not_annotated = []
    input_by_quid = sort_by_key(input_dicts, ['quid'])
    for d in question_dicts:
        quid = d['quid']
        if quid not in input_by_quid:
            questions_not_annotated.append(d)
    return questions_not_annotated


def get_annotated_questions(input_dicts, question_dicts):

    input_by_quid = sort_by_key(input_dicts, ['quid'])
    questions_by_quid = sort_by_key(question_dicts, ['quid'])
    questions_annotated = []
    for quid in input_by_quid:
        if quid in questions_by_quid:
            question = questions_by_quid[quid][0]
            questions_annotated.append(question)
    return questions_annotated


def collect_invalid(input_dicts, question_dicts):

    questions_by_pair = sort_by_key(question_dicts, ['property', 'concept'])
    questions_annotated = get_annotated_questions(input_dicts, question_dicts)
    questions_anntotated_by_pair = sort_by_key(questions_annotated, ['property', 'concept'])
    invalid_annotations = []

    for pair, questions_annotated in questions_anntotated_by_pair.items():
        questions = questions_by_pair[pair]
        if len(questions) != len(questions_annotated):
            #print('missing annotations for pair:', pair, len(questions), len(questions_annotated))
            invalid_annotations.extend(questions)
    return invalid_annotations

def get_available_questions(input_dicts, question_dicts):

    questions_for_annotation = []
    questions_not_annotated = collect_not_annotated(input_dicts, question_dicts)
    print('not annotated yet:', len(questions_not_annotated))
    invalid_annotations = collect_invalid(input_dicts, question_dicts)
    print('not valid', len(invalid_annotations))

    not_annotated_pair = sort_by_key(questions_not_annotated, ['property', 'concept'])
    invalid_pair = sort_by_key(invalid_annotations, ['property', 'concept'])

    for pair, questions in not_annotated_pair.items():
        if pair in invalid_pair:
            questions_for_annotation.extend(invalid_pair[pair])
        else:
            questions_for_annotation.extend(questions)
    test_for_wrong_questions(questions_for_annotation)
    return questions_for_annotation

def test_for_wrong_questions(questions_for_annotation):
    wrong_n_questions = []
    for_annotation_by_pair = sort_by_key(questions_for_annotation, ['property', 'concept'])
    for pair, questions in for_annotation_by_pair.items():
        if len(questions) > 10 or len(questions) < 3:
            wrong_n_questions.append((n, pair))
    assert len(wrong_n_questions) == 0, 'Number of questions per pair not correct.'



def get_check_and_test():
    checks = read_csv('../questions/checks.csv')
    tests = read_csv('../questions/tests.csv')

    rand_check = choice(checks)
    rand_test = choice(tests)
    tests_checks = [rand_check, rand_test]
    for d in tests_checks:
        if '' in d:
            d.pop('')
    return tests_checks

def get_batch(questions_to_annotate, n_qu = 70):
    batch = []
    properties = set()
    # shuffle questions:
    shuffle(questions_to_annotate)
    questions_by_pair = sort_by_key(questions_to_annotate, ['property', 'concept'])
    available_properties = set([p.split('-')[0] for p in questions_by_pair.keys()])

    for pair, questions in questions_by_pair.items():
        prop = pair.split('-')[0]
        if len(batch) < n_qu:
            if prop not in properties:
                #print('found a new one:', prop, len(batch))
                batch.extend(questions)
                properties.add(prop)
            else:
                props_not_used = available_properties.difference(properties)
                #print('properties not used:', len(props_not_used), len(batch))
                if len(props_not_used) > 0:
                    continue
                else:
                    batch.extend(questions)
                    properties.add(prop)
                    #print('no more properties, adding quetions:', len(questions))
        else:
            print('found enough questions', len(batch))
            break

    return batch


def batch_to_file(batch, url, experiment_name, run, n_qu, batch_n):

    header = ['quid', 'question', 'example_pos', 'example_neg']
    header_new = ['quid', 'description', 'exampleTrue', 'exampleFalse', 'triple', 'url']
    dirpath = f'../prolific_input/run{run}-group_{experiment_name}/'
    batch_name = f'qu{n_qu}-s_qu{n_qu}-batch{batch_n}'
    filepath = f'{dirpath}{batch_name}.csv'

    ### write header###
    header_path = f'{dirpath}header.txt'
    if not os.path.isfile(header_path):
        with open(header_path, 'w') as outfile:
            outfile.write(','.join(header_new))
    ###
    new_dicts = []
    for d in batch:
        triple = f"{d['relation']}-{d['property']}-{d['concept']}"
        new_d = dict()
        for h in header:
            new_d[h] = d[h]
        new_d['triple'] = triple
        new_d['url'] = url
        new_dicts.append(new_d)
    to_csv(filepath, new_dicts, header=False)
    return filepath


def create_new_batch(run, experiment_name, url, n_qu=70, test=False):

    input_dicts, batch_numbers = read_input(run, experiment_name)
    question_path = f'../questions/run{run}-all-restricted_True.csv'
    question_dicts = read_csv(question_path)
    selected_properties = read_group(experiment_name)
    test_check_questions = get_check_and_test()

    questions_to_annotate = get_available_questions(input_dicts, question_dicts)
    questions_in_selection = [d for d in questions_to_annotate \
                              if d['property'] in selected_properties]
    questions_in_selection_total = [d for d in question_dicts \
                              if d['property'] in selected_properties]

    ### Get counts ###
    # Total dataset
    n_total = len(question_dicts)
    n_not_annotated = len(questions_to_annotate)
    n_annotated = n_total - n_not_annotated
    percent_total = round(n_annotated/n_total, 3) * 100
    ###

    # Experiment group
    n_experiment_group = len(questions_in_selection_total)
    n_not_annotated_experiment_group = len(questions_in_selection)
    n_annotated_experiment_group = n_experiment_group - n_not_annotated_experiment_group
    percent_experiment_group = round(n_annotated_experiment_group/n_experiment_group, 3) * 100
    ###
    ###########

    # Create new batch
    highest_batch_number = max(batch_numbers)
    if test == False:
        current_batch_n = highest_batch_number + 1
    else:
        current_batch_n = 'TEST'
    new_batch = get_batch(questions_in_selection, n_qu = n_qu)
    # test for wrong number of questions
    test_for_wrong_questions(new_batch)
    # Add tests and checks (one randomly picked one each)
    new_batch.extend(test_check_questions)
    batch_path = batch_to_file(new_batch, url, experiment_name, run, n_qu, current_batch_n)

    print(f'Number of questions in the total dataset: {n_total}')
    print(f'Number of questions in {experiment_name}: {n_experiment_group}')
    print(f'Number of annotated questions: {n_annotated}\
    (of which in {experiment_name}: {n_annotated_experiment_group})')
    print(f'Percentage of annotated questions of the total: {percent_total}%')
    print(f'Percentage of annotated questions of {experiment_name}: {percent_experiment_group}%')
    print(f'Annotated {highest_batch_number} batches so far.')
    print(f'Created batch {current_batch_n} with {len(new_batch)} questions.')
    print(f'New batch written to: {batch_path}')
    pl_n = f'Agree or disagree (run{run}-{experiment_name}-batch{current_batch_n}-{n_qu}-{n_qu})'
    print(pl_n)


def main():
    run = 3
    experiment_name = 'experiment1'
    url = sys.argv[1]
    purpose = sys.argv[2]
    if purpose == 'test':
        test = True
    elif purpose == 'batch':
        test = False

    create_new_batch(run, experiment_name, url, n_qu=70, test = test)

if __name__ == '__main__':
    main()
