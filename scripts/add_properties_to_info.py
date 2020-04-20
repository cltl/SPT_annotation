import csv
import glob
from utils import read_csv, to_csv


def add_new_example_props():
    # Get property info
    path = '../data/property_info.csv'
    prop_dicts = read_csv(path)
    props_in_info = [d['property'] for d in prop_dicts]
    header = prop_dicts[0].keys()

    # Get example properties
    ex_files = glob.glob('../examples/*-pairs.csv')

    p_targets = ['prop_pos', 'prop_neg']
    for f in ex_files:
        with open(f) as infile:
            dl = read_csv(f)
        for d in dl:
            for t in p_targets:
                prop = d[t]
                if prop != '' and prop not in props_in_info:
                    print(f'"{prop}" needs annotation!')
                    new_d = dict()
                    new_d['property'] = prop
                    for h in header:
                        if h not in new_d:
                            new_d[h] = 'NEEDS INFO'
                    if new_d not in prop_dicts:
                        prop_dicts.append(new_d)
    print(f'Add info to added properties in: {path}')
    to_csv(path, prop_dicts)

if __name__ == '__main__':
    add_new_example_props()
