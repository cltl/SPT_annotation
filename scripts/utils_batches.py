import glob
from utils import read_csv

def read_input(run, experiment_name):
    all_input_dicts = []
    input_dicts_batch = []
    f_paths_all = glob.glob(f'../prolific_input/run*-group_*/*.csv')
    f_paths_run_name = glob.glob(f'../prolific_input/run{run}-group_{experiment_name}/*.csv')
    header_path = f'../prolific_input/run{run}-group_{experiment_name}/header.txt'
    batch_numbers = []
    # Get info current batch
    if os.path.isfile(header_path):
        with open(header_path) as infile:
            header = infile.read().split(',')
        for f in f_paths_run_name:
            input_dicts = read_csv(f, header = header)
            input_dicts_batch.extend(input_dicts)
            if 'TEST' not in f:
                f_name = f.split('/')[-1]
                batch_n = int(f_name.split('-')[2].split('.')[0][len('batch'):])
                ##../prolific_input/run3-group_experiment1/qu70-s_qu70-batch11.csv
                batch_numbers.append(batch_n)
        # get all input dicts:
        for f in f_paths_all:
            run = f.replace('../prolific_input/', '').split('-')[0]
            #../prolific_input/run3-group_experiment1/qu70-s_qu70-batch11.csv
            input_dicts = read_csv(f, header = header)
            all_input_dicts.extend(input_dicts)
    return all_input_dicts, input_dicts_batch, batch_numbers