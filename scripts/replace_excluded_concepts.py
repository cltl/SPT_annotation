import csv
import json
import math
from collections import Counter
import random
import numpy as np
import os
import sys

def load_general_bins():
    """
    Load the bins created in the original sampling code
    (copied from feature_data)
    :return: dict with bin information
    """
    with open('../vocabulary_data/bins_updated.json') as infile:
        bin_dict_general = json.load(infile)
    return bin_dict_general


def load_cosine_bins_prop(set_info_dict):
    """
    Load bins for cosine distances to centroid for a
    specific property
    :param set_info_dict:
    :return: dict (with cosine bins)
    """
    cosines = [float(d['cosine_centroid']) for c, d in set_info_dict.items()]
    values, bin_intervals = np.histogram(cosines, bins=3)
    bin_dict_cos = bins_to_dict('cosine_centroid', values, bin_intervals)
    return bin_dict_cos


def bins_to_dict(name, values, bin_intervals,
                 mapping=None, restriction=None,
                 bin_type='distribution'):
    """
    Turn cosine bin into bin dict
    :param name:
    :param values:
    :param bin_intervals:
    :param mapping:
    :param restriction:
    :param bin_type:
    :return: dict (with bin info in correct format)
    """

    bin_dict = dict()
    bin_dict[name] = {
        'type': bin_type,
        'mapping': mapping,
        'bins': [],
        'frequencies': [int(f) for f in list(values)],
        'restriction': restriction
    }

    for n, i in enumerate(bin_intervals):
        if n != len(bin_intervals) - 1:
            bin_dict[name]['bins'].append((i, bin_intervals[n + 1]))
        else:
            break
    return bin_dict


def get_concepts_set(p, col):
    """
    Given a property and collection, load the entire dataset
    of concepts associated with it.
    :param p: property
    :param col: collection
    :return: dict mapping a concept to its lexical and distributional
    information (dict)
    """
    concept_info_dict = dict()

    # original source of lexical data:
    #path = f'../data_all_candidates/concepts_additional_info/{col}/{p}.csv'
    # added lexical info for concepts added in the manual filtering process:
    path = f'../data_all_candidates/concepts_additional_info_manual_run5_pilot/{col}/{p}.csv'

    with open(path) as infile:
        reader = csv.DictReader(infile)
        dicts = list(reader)

    for d in dicts:
        concept = d['lemma']
        filter_dec = d['filter']
        source = d['sources_str']
        if filter_dec == 'True':
            concept_info_dict[concept] = d
        elif filter_dec == 'False' and 'manually_included' in source:
            concept_info_dict[concept] = d
    return concept_info_dict


def get_excluded_included_concepts(p):
    """
    Load concepts annotated for exclusion.
    (We annotated instances that would hinder the
    annotation task and not yield interesting information.)
    :param p: the property
    :return: list of concept dicts exlcuded, list of concept dicts included
    """
    path = f'../data_pair_filtering/aggregated/experiment3/{p}.csv'

    with open(path) as infile:
        concept_dicts_total = list(csv.DictReader(infile, delimiter='\t'))
    concept_dicts_exclude = [d for d in concept_dicts_total
                             if d['decision'].startswith('exclude')]
    concept_dicts_include = [d for d in concept_dicts_total if d['decision'] == 'include']
    concept_dicts_added =[d for d in concept_dicts_total if d['decision'] == 'added']
    print('overview')
    print('include', len(concept_dicts_include))
    print('exclude', len (concept_dicts_exclude))
    print('added', len(concept_dicts_added))
    print('total:', len(concept_dicts_total))
    print()
    return concept_dicts_exclude, concept_dicts_include, concept_dicts_added


def assign_to_bin(concept_dict, bin_dict, name):
    """
    Assign bin information to concepts for a specific
    lexical aspect
    :param concept_dict:
    :param bin_dict:
    :param name: lexical aspect (e.g. polysemy, frequency, etc.)
    :return: target_bin
    """
    target_bin = None
    if name == 'polysemy':
        concept_value = get_polysemy_info(concept_dict)
        target_bin = concept_value
    else:
        if concept_dict[name] != '':
            concept_value = float(concept_dict[name])
            if bin_dict[name]['mapping'] == 'log':
                concept_value = math.log(concept_value)
            n_bins = len(bin_dict[name]['bins'])
            for n, interval in enumerate(bin_dict[name]['bins']):
                start, end = interval
                if n < (n_bins - 1):
                    if start <= concept_value < end:
                        target_bin = n
                        break
                    else:
                        target_bin = None
                else:
                    if start <= concept_value <= end:
                        target_bin = n
                        break
                    else:
                        target_bin = None
        else:
            target_bin = None
    return target_bin


def get_polysemy_info(concept_dict):
    """
    Extract polysemy bin from lexical data
    :param concept_dict:
    :return: str (polysemy label)
    """
    mipvu_met = concept_dict['mipvu']
    polysemy_type = concept_dict['polysemy_type']

    if polysemy_type == 'mon':
        poly = 'mon'
    elif polysemy_type == 'homonyms_also_same_pos':
        poly = 'homonym'
    elif mipvu_met == 'True' or mipvu_met == 'true':
        poly = 'met'
    # Possibly metonymy if not metaphor and not homonym
    # caveat: the metaphor annotations are not exhaustive
    elif polysemy_type == 'poly':
        poly = 'poly_metonymy'
    else:
        poly = None
    return poly


def get_bin_feature_dict(general_bin_dict, concept_dicts):
    """
    Create dict mapping concepts to all bins
    :param general_bin_dict:
    :param concept_dicts:
    :return: dict (mapping concepts to features (dict))
    """
    concept_features_dict = dict()
    for concept_dict in concept_dicts:
        features_dict = dict()
        concept = concept_dict['lemma']
        for name in general_bin_dict.keys():
            target_bin = assign_to_bin(concept_dict, general_bin_dict, name)
            features_dict[name] = target_bin
        features_dict['label'] = concept_dict['label']
        concept_features_dict[concept] = features_dict
    return concept_features_dict


def get_ranked_bin_imbalances(general_bin_dict,
                              set_bin_features,
                              concepts_selected,
                              include_overrepresented_bins=False):
    """
    Calculate the difference between the expected number
    of concepts in a bin and the actual number (in percent).
    :param general_bin_dict:
    :param set_bin_features:
    :param concepts_selected:
    :return: list of tuples (bin info) sorted from highest to smallest difference
    to expected number of concepts in a bin.
    """
    n_concepts = len(concepts_selected)
    bin_diff_tuples = []
    for name in general_bin_dict:
        bin_concept_cnt = Counter()
        bin_dict = general_bin_dict[name]
        bins_expected = bin_dict['bins']
        n_bins = len(bins_expected)
        n_equal_distribution = n_concepts / n_bins
        print(name, len(bins_expected))
        print('expected number of concepts in a single bin:', n_equal_distribution, 'out of', n_concepts)
        for concept in concepts_selected:
            f = set_bin_features[concept][name]
            bin_concept_cnt[f] += 1
        for bin_name, cnt in bin_concept_cnt.items():
            diff_to_equal = n_equal_distribution - cnt
            diff_to_equal_percent = diff_to_equal / n_concepts
            if include_overrepresented_bins:
                # include all bins in case there are no concepts from the imbalanced bins:
                bin_diff_tuples.append((diff_to_equal_percent, name, bin_name))
            else:
                if diff_to_equal > 0:
                    bin_diff_tuples.append((diff_to_equal_percent, name, bin_name))
    # sort from biggest to smallest:
    sorted_diff_name_tuples = sorted(bin_diff_tuples, reverse=True)
    return sorted_diff_name_tuples


def find_equivalents(set_bin_features, concepts_not_selected, concept_dicts_exclude):
    """
    Find direct equivalents for excluded concepts.
    :param set_bin_features:
    :param concepts_not_selected:
    :param concept_dicts_exclude:
    :return: set (concepts found for direct replacement)
    """
    replacement_concepts = set()
    features_not_selected = dict()
    for concept in concepts_not_selected:
        features_not_selected[concept] = set_bin_features[concept]

    for d in concept_dicts_exclude:
        concept = d['lemma']
        features = set_bin_features[concept]
        if features in features_not_selected.values():
            for concept_available, feats_available in features_not_selected.items():
                if features == feats_available:
                    replacement_concepts.add(concept_available)
                    break
    return replacement_concepts


def resample_missing_concepts(n_to_replace,
                              concepts_not_selected,
                              concepts_selected,
                              general_bin_dict,
                              set_bin_features,):
    """
    Use bin imbalances to draw new candidate concepts. Fill set
    until enough concepts have been collected.
    :param n_to_replace: either number of conepts to replace or higher.
    This can be used to  increase the number of concepts in a set.
    :param concepts_not_selected:
    :param concepts_selected:
    :param general_bin_dict:
    :param set_bin_features:
    :return:
    """
    replacement_concepts = set()
    bins_sorted = get_ranked_bin_imbalances(general_bin_dict,
                                            set_bin_features,
                                            concepts_selected)
    concepts_available = concepts_not_selected
    while len(replacement_concepts) < n_to_replace and len(concepts_available) > 0:
        # get bin overview
        for bin_tuple in bins_sorted:
            if len(replacement_concepts) == n_to_replace or len(concepts_available) == 0:
                print('found enough!')
                break
            name = bin_tuple[1]
            bin_name = bin_tuple[2]
            concepts_not_selected_shuff = list(concepts_not_selected)
            random.shuffle(concepts_not_selected_shuff)
            # TODO make this replicable
            # shuffle original concept list so it's not sorted by cosine distance
            found_concept = False
            for c in concepts_not_selected_shuff:
                features = set_bin_features[c]
                if len(replacement_concepts) == n_to_replace or len(concepts_available) == 0:
                    print('already found enough!')
                    break
                if features[name] == bin_name:
                    print('replacement found in ', name, bin_name)
                    replacement_concepts.add(c)
                    concepts_available.remove(c)
                    found_concept = True
                    # only draw one concept per iteration:
                    break
        print('iterated over all bins. found concept:',  found_concept)
        concepts_selected.update(replacement_concepts)
        # re-evaluate bin imbalance
        if found_concept == True:
            bins_sorted = get_ranked_bin_imbalances(general_bin_dict, set_bin_features, concepts_selected)
        else:
            print('no longer enough underrepresented bins available')
            bins_sorted = get_ranked_bin_imbalances(general_bin_dict, set_bin_features,
                                                    concepts_selected, include_overrepresented_bins=True)
    return replacement_concepts


def get_concept_dicts(p, concepts, set_info_dict):
    """
    Collect concept info for new concepts
    :param p:
    :param concepts:
    :param set_info_dict:
    :return:
    """
    # get concept info for replacement concepts
    cols = ['lemma', 'label', 'certainty', 'sources_str']
    concept_dicts = []
    for c in concepts:
        # get general lexical info dict
        lexical_info = set_info_dict[c]
        concept_dict = dict()
        for col in cols:
            concept_dict['property'] = p
            concept_dict[col] = lexical_info[col]
        concept_dicts.append(concept_dict)
    return concept_dicts


def replacements_to_file(p, run, concept_dicts_new, concept_dicts_exclude):
    """
    Write exluded concepts and replacement concepts to file.
    :param p:
    :param concept_dicts_new:
    :param concept_dicts_exclude:
    :return: None
    """
    path = f'../data_pair_filtering/concept-replacement/run{run}/'
    if not os.path.isdir(path):
        os.mkdir(path)
    header = concept_dicts_exclude[0].keys()
    print('header:', header)
    with open(f'{path}{p}-excluded.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, delimiter='\t', fieldnames=header)
        for d in concept_dicts_exclude:
            writer.writerow(d)
    header = concept_dicts_new[0].keys()
    print('header:', header)
    with open(f'{path}{p}-replacement.csv', 'w') as outfile:
        writer = csv.DictWriter(outfile, delimiter='\t', fieldnames=header)
        for d in concept_dicts_new:
            writer.writerow(d)


def main():
    p = sys.argv[1]
    col = sys.argv[2]
    run = sys.argv[3]
    # make sure we have enough data:
    n_concepts_expected = 180
    # props_collection_dict = {'used_in_cooking': 'complex', 'warm': 'perceptual', 'black': 'perceptual'}
    # col = props_collection_dict[p]
    set_info_dict = get_concepts_set(p, col)
    # harmonize undecided labels to neg/pos (instead of pos/neg):
    for concept, d in set_info_dict.items():
        label = d['label']
        if label in ['pos/neg', 'neg/pos']:
            d['label'] = 'neg/pos'
    # load annotations for exclusion:
    concept_dicts_exclude, concept_dicts_include, concept_dicts_added = get_excluded_included_concepts(p)
    # Get selected concepts
    # manually added concepts should be treated as already included (and serve as a basis for resampling):
    print('before adding added:', len(concept_dicts_include))
    concept_dicts_include = concept_dicts_include + concept_dicts_added
    print('after adding added:', len(concept_dicts_include))
    concept_dicts_total = concept_dicts_include + concept_dicts_exclude
    concepts_selected = set([d['lemma'] for d in concept_dicts_total])
    # get concepts still available for sampling:
    total_concepts = set(set_info_dict.keys())
    concepts_not_selected = total_concepts.difference(concepts_selected)

    # there should be no intersection between selected and still available concepts:
    # assert len(set_info_dict) > len(concept_dicts_total), 'No more concepts for sampling available'
    assert len(concepts_selected.intersection(concepts_not_selected)) == 0,\
        'overlap in exlcuded and available concepts!'
    print('test 1 complete')

    # get bins and add consines to general bin dict
    general_bin_dict = load_general_bins()
    bin_dict_cosine = load_cosine_bins_prop(set_info_dict)
    general_bin_dict.update(bin_dict_cosine)

    # assign bin data to concepts in dataset
    set_bin_features = get_bin_feature_dict(general_bin_dict, set_info_dict.values())
    # get direct replacements for excluded concepts:
    direct_replacements = find_equivalents(set_bin_features,
                                           concepts_not_selected,
                                           concept_dicts_exclude)
    # add to already selected concepts:
    concepts_selected.update(direct_replacements)
    # update concepts still available:
    concepts_not_selected = total_concepts.difference(concepts_selected)
    # determine  how many concepts still need replacement
    # Use this to fill up the dataset to 180 items:
    n_concepts_include = len(concept_dicts_include) + len(direct_replacements)
    n_to_replace = n_concepts_expected - n_concepts_include
    print('Concepts included before re-sampling (not excluded + direct equivalents:', n_concepts_include)
    print('Concepts to find:', n_to_replace)
    # add labels to general bin dict so we also check positive and negative candidates
    general_bin_dict['label'] = {'bins': ['pos', 'neg', 'neg/pos']}


    # determine bin imbalances and resample based on them:

    resampled_concepts = resample_missing_concepts(n_to_replace,
                                                   concepts_not_selected,
                                                   concepts_selected,
                                                   general_bin_dict,
                                                   set_bin_features)

    # check if enough concepts were found
    new_concepts = set()
    new_concepts.update(direct_replacements)
    new_concepts.update(resampled_concepts)

    # write to file
    # add added concepts to new concepts:
    added_concepts_set = [d['lemma'] for d in concept_dicts_added]
    new_concepts.update(added_concepts_set)
    concept_dicts_new = get_concept_dicts(p, new_concepts, set_info_dict)
    concepts_replaced = [d['lemma'] for d in concept_dicts_exclude]
    concept_dicts_replaced = get_concept_dicts(p, concepts_replaced, set_info_dict)
    replacements_to_file(p, run, concept_dicts_new, concept_dicts_replaced)

if __name__ == '__main__':
    main()
