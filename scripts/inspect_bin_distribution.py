from utils import read_pairs
from replace_excluded_concepts import get_concepts_set
from replace_excluded_concepts import load_general_bins
from replace_excluded_concepts import load_cosine_bins_prop
from replace_excluded_concepts import get_bin_feature_dict

from collections import Counter
import sys
import os


def get_bin_distributions(general_bin_dict,
                              set_bin_features,
                              concept_dicts):
    """

    :param general_bin_dict: represents bins
    :param set_bin_features: words in the dataset with bin info
    :param concept_dicts: the concepts to analyze
    :return: dict with distribution over bins
    """
    # get total #concepts so we can use percentages
    n_concepts = len(concept_dicts)
    bin_distribution = dict()
    for name in general_bin_dict:
        bin_concept_cnt = Counter()
        # n_bins = len(general_bin_dict[name]['bins'])
        for d in concept_dicts:
            concept = d['lemma']
            f = set_bin_features[concept][name]
            bin_concept_cnt[f] += 1
        bin_distribution[name] = bin_concept_cnt
    for name, distribution in bin_distribution.items():
        bin_dict = general_bin_dict[name]
        bin_type = bin_dict['type']
        if bin_type == 'categories':
            bins_expected = bin_dict['bins']
        else:
            bins_expected = list(range(len(bin_dict['frequencies'])))
        for b in distribution:
            if b not in bins_expected:
                bins_expected.append(b)
        for b in bins_expected:
            if b in distribution:
                cnt = distribution[b]
                percent = cnt/n_concepts
            else:
                cnt = 0
                percent = 0
            distribution[b] = (round(percent, 2), cnt)

    return bin_distribution


def main():
    # Load data

    target_property = sys.argv[1]
    target_collection = sys.argv[2]
    dir_path = '../analysis/bin_distribution/'
    results_path = f'{dir_path}{target_property}.txt'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    pairs_original = read_pairs(target_collection, source='original')
    pairs_resampled = read_pairs(target_collection, source='resampled')

    concepts_original = pairs_original[target_property]
    concepts_resampled = pairs_resampled[target_property]

    # sort data into bins
    set_info_dict = get_concepts_set(target_property, target_collection)
    general_bin_dict = load_general_bins()
    bin_dict_cosine = load_cosine_bins_prop(set_info_dict)
    general_bin_dict.update(bin_dict_cosine)

    # assign bin data to concepts in dataset
    set_bin_features = get_bin_feature_dict(general_bin_dict, set_info_dict.values())

    distribution_original = get_bin_distributions(general_bin_dict,
                                                  set_bin_features,
                                                  concepts_original)

    distribution_resampled = get_bin_distributions(general_bin_dict,
                                                   set_bin_features,
                                                   concepts_resampled)


    with open(results_path, 'w') as outfile:
        for name, d_original in distribution_original.items():
            outfile.write(f'\n{name}\n')
            outfile.write('bin\t original (percent)\t original (absolut)\tresampled (percent)\tresampled (absolut)\n')
            d_resampled = distribution_resampled[name]
            for b, percent_original in d_original.items():
                if b in d_resampled:
                    percent_resampled = d_resampled[b]
                else:
                    percent_resampled = (0, 0)
                outfile.write(f'{b}\t{percent_original[0]} \t{percent_original[1]}\t{percent_resampled[0]}\t{percent_resampled[1]}\n\n')

    print('Results written to:', results_path)

if __name__ == '__main__':
    main()
