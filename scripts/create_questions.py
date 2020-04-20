import uuid
import sys

from utils import read_template
from utils import read_property_info
from utils import read_examples
from utils import get_example
from utils import create_question
from utils import read_pairs
from utils import get_levels
from utils import to_csv

class Pairs:

    def __init__(self, run, restrict = True):
        self.run = run
        self.collections = ['perceptual', 'activities', 'complex', 'parts']
        self.data_dicts = self.get_data_dicts()
        self.question_templates, self.level_dict = read_template(run)
        self.relations = [rel for rel_list in self.level_dict.values()\
                          for rel in rel_list]
        self.prop_info = read_property_info()
        self.relation_examples_dict = read_examples(self.relations)
        self.restrict = restrict
        self.questions = self.get_questions()

    def get_data_dicts(self):
        data_dicts = []
        for coll in self.collections:
            prop_data_dicts = read_pairs(coll)
            for prop, dicts in prop_data_dicts.items():
                for d in dicts:
                    d['concept'] = d['lemma']
                    d.pop('lemma')
                    d['collection'] = coll
                    d['sources'] = d['sources_str']
                    d.pop('sources_str')
                data_dicts.extend(dicts)
        return data_dicts

    def get_questions(self):
        questions = []
        for d in self.data_dicts:
            certainty = d['certainty']
            label = d['label']
            levels = get_levels(label, certainty, self.restrict)
            for l in levels:
                relations = self.level_dict[l]
                for rel in relations:
                    coll = d['collection']
                    prop = d['property']
                    if prop.startswith('made_of_'):
                        print(prop)
                        coll = 'parts_material'
                    scale = self.prop_info[prop][0]['scale']
                    if scale == 'T':
                        coll = coll+'_scale'
                    coll_rel = (coll, rel)
                    if coll_rel in self.question_templates:
                        q_d = dict()
                        q_d.update(d)
                        qu_temp = self.question_templates[coll_rel]
                        cat = self.prop_info[prop][0]['category']
                        q_d['quid']  = uuid.uuid4()
                        q_d['relation'] = rel
                        q_d['question'] = create_question(prop, d['concept'], qu_temp, cat)
                        examples = self.relation_examples_dict[rel][coll]
                        ex_dict = get_example(examples, qu_temp, self.prop_info, rel)
                        q_d.update(ex_dict)
                        questions.append(q_d)
        return questions

    def to_file(self):
        #questions/run_3-all-restrict_True.csv
        filepath = f'../questions/run{self.run}-all-restricted_{self.restrict}.csv'
        to_csv(filepath, self.questions)
        print(f'{len(self.questions)} questions written to: {filepath}')


if __name__ == '__main__':
    run = sys.argv[1]
    restrict = True
    pairs =  Pairs(run,  restrict = True)
    print(len(pairs.questions))
    pairs.to_file()
