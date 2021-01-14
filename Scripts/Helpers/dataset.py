import csv
from datetime import datetime
import glob
import json
import random
import re

from Helpers.cyrillic import to_latin


def create_dataset(indexes: list, wiki_docs: list, categories, out_path):
    """Creates a csv dataset in format of [doc_id, category1, category2 ... categoryN, doc_text], where doc belonging to
    certain category is marked with 1, or 0 otherwise. This is a format that ktrain supports for multi-label
    classification. Logic iterates through WikiExtractor-processed files and reads docs. It will store the information
    that a doc belongs to categories of interest, defined in categories file. Docs are trimmed to a 130k length, since
    csv library fails on very long rows. This happens. Resulting dataset is shuffled as train and validation sets
    are got simply by splitting a list."""
    categories = json.loads(open(categories, 'r', encoding='utf-8').read())
    category_columns = list(categories)
    category_columns_set = set(category_columns)

    csv_lines = []

    for i in range(len(wiki_docs)):
        index = indexes[i]
        wiki_files = glob.glob(wiki_docs[i] + '/*')
        for wiki_file in wiki_files:
            print(f'{datetime.now()} - reading {wiki_file}')
            file = open(wiki_file, 'r', encoding='utf-8')
            line = file.readline()
            while line != '':
                if '<doc id="' in line:
                    doc_id = get_id(line)
                    found_categories = list()
                    for root_category in categories:
                        for wiki_category in categories[root_category]:
                            if wiki_category in index and doc_id in index[wiki_category]:
                                if root_category not in found_categories:
                                    found_categories.append(root_category)
                    matches_categories = not category_columns_set.isdisjoint(found_categories)
                    if matches_categories:
                        flags = list(map(lambda c: ('1' if c in found_categories else '0'), category_columns))
                        docs = get_doc(file)
                        for doc in docs:
                            row = [doc_id]
                            row.extend(flags)
                            row.extend([clean(to_latin(str.replace(doc, '\n', '')))])
                            if len(doc) < 130_000:
                                csv_lines.append(row)

                line = file.readline()

    print(f'{datetime.now()} - writing index to {out_path}')
    file_out = open(out_path, 'w', encoding='utf-8', newline='')
    output = csv.writer(file_out)
    header = ['id']
    header.extend(category_columns)
    header.extend(['text'])
    output.writerow(header)
    random.shuffle(csv_lines)
    for doc in csv_lines:
        output.writerow(doc)
    file_out.close()


def get_id(doc_line):
    """Extracts doc id from the declaring line in WikiExtractor-extracted format."""
    return re.sub('".*$', '', str.replace(doc_line, '<doc id="', '', ), flags=re.DOTALL)


def clean(doc):
    """Performs a set of cleaning and trimming that I found helpful, which aren't covered by what WikiExtractor does."""
    clean_doc = re.sub('(__[A-ZŽĐŠČĆ]+__)|(-{)|(}-)|(\\(\\))|(\\(,\\s\\))', '', doc)
    clean_doc = re.sub('\\s+', ' ', clean_doc)
    return clean_doc.lstrip()


def get_doc(wiki_file):
    """Takes the file reader and reads a single wiki doc. Doesn't return anything if the doc is too short. This helps
    remove a lot of non-informative articles and generally helps. Can return multiple docs, which I tried by making
    each paragraph a doc. This was counter-productive, as isolated paragraphs very often lose the topic that the parent
    doc has."""
    line = wiki_file.readline()
    doc = ''
    while '</doc>' not in line:
        doc += ' ' + line.rstrip('\n')
        line = wiki_file.readline()
    if len(doc) > 200:
        return [doc]
    else:
        return []


def load_dataset_csv(file_path, val_ratio: int, category_count: int):
    """Loads a multi-label dataset. Returns data split into training and validation compatible with
    ktrain.text.Transformer. val_ratio works on i % val_ratio == 0, so 5 means 20%. Sue me."""
    training_texts = []
    training_labels = []
    validation_texts = []
    validation_labels = []

    doc_i = 0
    for entry in csv.reader(open(file_path, 'r', encoding='utf-8')):
        doc_i += 1
        if doc_i == 1:
            continue
        text = entry[category_count + 1]
        labels = list(map(int, entry[1:category_count + 1]))
        if doc_i % val_ratio == 0:
            validation_texts.append(text)
            validation_labels.append(labels)
        else:
            training_texts.append(text)
            training_labels.append(labels)

    return training_texts, training_labels, validation_texts, validation_labels
