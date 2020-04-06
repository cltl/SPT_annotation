from utils import read_template
from utils import to_csv


def get_relations(run):
    dicts = []
    filepath = f'../templates/relation_overview_run{run}.csv'
    collection_relation_question_dict, level_relation_dict = read_template(run)
    for l, rels, in level_relation_dict.items():
        l = int(l)
        if l == 1:
            l_name = 'all'
        elif l == 2:
            l_name = 'some'
        elif l == 3:
            l_name = 'few'
        for r in rels:
            d = dict()
            if r == 'creative':
                 d['level'] = 'creative'
            else:
                d['level'] = l_name
            d['relation'] = r
            dicts.append(d)
    to_csv(filepath, dicts, header = True)


if __name__ == '__main__':
    run = 3
    get_relations(run)
