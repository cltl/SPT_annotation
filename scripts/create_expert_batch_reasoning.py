import sys

from utils import read_csv, to_csv
from utils import sort_by_key

from create_batch import batch_to_file
from create_batch import print_task_intro

# get selected pairs:




def main():
    group = sys.argv[1]
    #group = 'expert_inspection1'
    run = sys.argv[2]
    n_qu = sys.argv[3]


    #run = 4

    experiment_name = group
    batch_n = 1
    current_batch_n = batch_n
    task_name =  f'Agree or disagree (run{run}-{experiment_name}-batch{current_batch_n}-{n_qu}-{n_qu})'
    print(task_name)
    whitelist = print_task_intro(run)

if __name__ == '__main__':
    main()
