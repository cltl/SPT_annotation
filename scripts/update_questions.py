# updating examples

from utils import read_csv, to_csv


def update_examples(question_dicts, label, ex_dict, rel):
    for d in question_dicts:
        if d[f'concept_{label}'] == ex_dict['concept_old'] \
        and d[f'prop_{label}'] == ex_dict['prop_old'] and d['relation'] == rel:
            ex = d[f'example_{label}']
            print('old', ex)
            d[f'concept_{label}'] = ex_dict['concept_new']
            d[f'prop_{label}'] = ex_dict['prop_new']
            new_ex =  ex.replace(ex_dict['concept_old'], ex_dict['concept_new'])
            new_ex =  new_ex.replace(ex_dict['prop_old'], ex_dict['prop_new'])
            if new_ex[-1] != '.':
                new_ex = new_ex+'.'
            d[f'example_{label}'] = new_ex
            print('new', d[f'example_{label}'])
    to_csv(path, question_dicts)


def add_quot_marks(question_dicts, path, rel = 'creative'):
    relevant_keys = ['question', 'example_pos', 'example_neg']
    for d in question_dicts:
        if d['relation'] == rel:
            for k in relevant_keys:
                phrase = d[k]
                print(phrase)
                phrase = phrase.replace('say (a/an)', 'say ``(a/an)')
                phrase = phrase.replace(', but I', '", but I')
                print(phrase)
                d[k] = phrase
    to_csv(path, question_dicts)


if __name__ == '__main__':

    ex_dict = {}
    ex_dict['prop_old'] = 'party'
    ex_dict['concept_old'] = 'student'
    ex_dict['prop_new'] = 'swim'
    ex_dict['concept_new'] = 'rock'

    path = '../questions/run3-all-restricted_True.csv'
    question_dicts = read_csv(path)

    rel = 'rare'
    label = 'neg'
    #update_examples(question_dicts, label, ex_dict, rel)
    #add_quot_marks(question_dicts, path, rel = 'creative')
