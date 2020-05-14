import sys

from utils import read_csv, to_csv
from utils import sort_by_key

from create_batch import batch_to_file
from create_batch import print_task_intro

# get selected pairs:

def get_pairs(group):
    with open(f'../experiment_groups/{group}.txt') as infile:
        pairs = infile.read().strip().split('\n')
    return pairs

def create_inspection_batch(group, run):
    pairs = get_pairs(group)
    question_path = f'../questions/run{run}-all-restricted_True.csv'
    question_dicts = read_csv(question_path)
    questions_by_pair = sort_by_key(question_dicts, ['property', 'concept'])

    inspection_questions = []
    for p in pairs:
        questions = questions_by_pair[p]
        inspection_questions.extend(questions)
    return inspection_questions


def main():
    group = sys.argv[1]
    #group = 'expert_inspection1'
    run = sys.argv[2]
    #run = 4
    inspection_questions = create_inspection_batch(group, run)
    n_qu = len(inspection_questions)
    experiment_name = group
    batch_n = 1
    current_batch_n = batch_n
    batch = inspection_questions
    url = 'test'
    task_name =  f'Agree or disagree (run{run}-{experiment_name}-batch{current_batch_n}-{n_qu}-{n_qu})'
    batch_to_file(batch, url, experiment_name, run, n_qu, batch_n)
    print(task_name)
    whitelist = print_task_intro(run)

if __name__ == '__main__':
    main()
