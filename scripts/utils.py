# utils

import csv
from collections import defaultdict
import random
import os


def read_csv(filepath, header=None):
    # check for separator
    with open(filepath) as infile:
        lines = infile.read().split('\n')
    if '\t' in lines[0]:
        sep = '\t'
    else:
        sep = ','
    with open(filepath) as infile:
        if not header:
            dict_list = list(csv.DictReader(infile, delimiter=sep))
        else:
            dict_list = list(csv.DictReader(infile, delimiter=sep,
                                            fieldnames=header))
    return dict_list


def sort_by_key(data_dict_list, keys):
    sorted_dict = defaultdict(list)
    for d in data_dict_list:
        if len(keys) == 1:
            key = keys[0]
            sortkey = d[key].strip()
        else:
            sortkeys = []
            for key in keys:
                sortkey = d[key].strip()
                sortkeys.append(sortkey)
            sortkey = '-'.join(sortkeys)
        sorted_dict[sortkey].append(d)
    return sorted_dict


def read_examples(relations):
    relation_examples_dict = dict()
    for rel in relations:
        filepath = f'../examples/{rel}-pairs.csv'
        dict_list = read_csv(filepath)
        sorted_by_collection = sort_by_key(dict_list, ['collection'])
        relation_examples_dict[rel] = sorted_by_collection
    return relation_examples_dict


def read_pairs(collection, run, source = 'resampled'):
    if source == 'resampled':
        filepath = f'../data/{source}/run{run}/{collection}.csv'
    else:
        filepath = f'../data/{source}/{collection}.csv'
    if os.path.isfile(filepath):
        dict_list = read_csv(filepath)
        dict_list_by_prop = sort_by_key(dict_list, ['property'])
    else:
        dict_list_by_prop = dict()
    return dict_list_by_prop


def read_property_info():
    filepath = f'../data/property_info.csv'
    dict_list = read_csv(filepath)
    prop_info_dict = sort_by_key(dict_list, ['property'])
    return prop_info_dict


def read_template(run):
    filepath = f'../templates/template-run{run}.csv'
    dict_list = read_csv(filepath)
    collections = ['perceptual', 'perceptual_scale', 'complex',
                   'complex_scale', 'parts', 'parts_material',
                   'activities']

    collection_relation_question_dict = dict()
    level_relation_dict = defaultdict(set)
    for d in dict_list:
        target_collections = [c for c in collections if d[c].strip("'") == '1']
        relation = d['relation']
        level = d['level']
        if level != '':
            level = int(level)
            level_relation_dict[level].add(relation)
        for c in target_collections:
            collection_relation_question_dict[(c, relation)] = d['question']
    assert len(collection_relation_question_dict) == 70, 'not enough relations'
    assert len(level_relation_dict[1]) == 6, 'wrong mapping level 1'
    assert len(level_relation_dict[2]) == 2, 'wrong mapping level 2'
    assert len(level_relation_dict[3]) == 4, 'wrong mapping level 3'
    return collection_relation_question_dict, level_relation_dict


def capitalize(word):
    if len(word) > 1:
        cap = word[0].upper() + word[1:]
    else:
        cap = word
    return cap


def verb_agreement(prop):
    prop_s = f'{prop}s'
    prop_ing = f'{prop}ing'

    if prop == 'lay_eggs':
        prop_s = 'lays eggs'
        prop_ing = 'laying eggs'
    elif prop == 'fly':
        prop_s = 'flies'
    elif prop == 'swim':
        prop_ing = 'swimming'
    elif prop == 'breathe':
        prop_ing = 'breathing'
    elif prop == 'cut':
        prop_ing = 'cutting'
    elif prop == 'wrap':
        prop_ing = 'wrapping'
    return prop_s, prop_ing


def create_question(prop, concept, question_temp, category):
    prop_s, prop_ing = verb_agreement(prop)
    prop_cap = capitalize(prop)
    concept_cap = capitalize(concept)
    # category = prop_info[prop][0]['category']
    prop = prop.strip()

    replacements = [
        ('[X]', prop),
        ('[CX]', prop_cap),
        ('[Xs]', prop_s),
        ('[Xing]', prop_ing),
        ('[Y]', concept),
        ('[CY]', concept_cap),
        ('[category]', category),
    ]

    for char, replace_form in replacements:
        question_temp = question_temp.replace(char, replace_form)
        question_temp = question_temp.replace('???', '"')
    question = question_temp
    return question


def get_levels(label, certainty, restrict):
    if restrict == True:
        if certainty in ['uncertain', 'not_certain', 'not certain']:
            levels = [1, 2, 3]
        else:
            if label == 'pos':
                levels = [1, 2]
            else:
                levels = [3]
    else:
        levels = [1, 2, 3]
    return levels


def get_example_single(examples, question_temp, prop_info_dict):
    rand_index = random.randint(0, len(examples) - 1)
    rand_example = examples[rand_index]
    if 'collection' in rand_example:
        rand_example.pop('collection')
    labels = ['pos', 'neg']
    for label in labels:
        prop = rand_example[f'prop_{label}']
        concept = rand_example[f'concept_{label}']
        # print(prop)
        # print(prop_info_dict[prop])
        category = prop_info_dict[prop][0]['category']
        example_qu = create_question(prop, concept, question_temp, category)
        rand_example[f'example_{label}'] = example_qu
    return rand_example


def get_example_creative(examples, question_temp, prop_info_dict):
    creative_ex_d = defaultdict(list)
    ex_str_dict = dict()
    labels = ['pos', 'neg']
    for ex in examples:
        for k, v in ex.items():
            creative_ex_d[k].append(v)
        for label in labels:
            prop = ex[f'prop_{label}']
            concept = ex[f'concept_{label}']
            category = prop_info_dict[prop][0]['category']
            example_qu = create_question(prop, concept, question_temp, category)
            creative_ex_d[f'example_{label}'].append(example_qu)
    for k, v_list in creative_ex_d.items():
        ex_str_dict[k] = '\n'.join(v_list)
    return ex_str_dict


def read_group(exp_name):
    collections = ['perceptual', 'activities', 'parts', 'complex']
    prop_coll_dict = dict()
    for c in collections:
        filepath = f'../experiment_groups/{c}-group_{exp_name}.txt'
        if os.path.isfile(filepath):
            with open(filepath) as infile:
                properties = infile.read().strip().split('\n')
            for prop in properties:
                prop_coll_dict[prop] = c
    return prop_coll_dict


def get_example(examples, question_temp, prop_info_dict, relation):
    if relation != 'creative':
        example_dict = get_example_single(examples, question_temp, prop_info_dict)
    else:
        example_dict = get_example_creative(examples, question_temp, prop_info_dict)
    return example_dict


def to_csv(filepath, dict_list, header=True):
    fieldnames = dict_list[0].keys()
    with open(filepath, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames,
                                delimiter='\t')
        if header == True:
            writer.writeheader()
        for d in dict_list:
            writer.writerow(d)
