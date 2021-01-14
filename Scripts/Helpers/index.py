import json
import re

from Helpers.cyrillic import to_latin


def create_index(input_path, output_path, category_string, generate_index_cardinality_list: bool):
    """Creates a category to doc id mappings in json format. It reads through xml file as a txt file and identifies
    category list for each doc, storing the information. With generate_index_cardinality_list enabled, it also generates
    a txt file with doc count for each category. You can use the txt to determine what's worth using, but it was
    generally useful only at start. Index is dependent on wiki files used, and it's reusable for any sort of category
    related processing."""
    file = open(input_path, 'r', encoding="utf-8")
    index = dict()
    doc_id = -1
    look_for_id = False
    line = file.readline()
    while line != '':
        if '<page>' in line:
            look_for_id = True
        if '<id>' in line and look_for_id:
            doc_id = re.sub('^.*<id>', '', re.sub('</id>.*$', '', line, flags=re.DOTALL), flags=re.DOTALL)
            look_for_id = False
        if f'[[{category_string}' in line and '<' not in line:
            categories = categories_from_line(line, category_string)
            for category in categories:
                if category not in index:
                    index[category] = list()
                index[category].append(doc_id)
        line = file.readline()

    with open(output_path, 'w', encoding="utf-8") as outFile:
        outFile.write(json.dumps(index, sort_keys=True, indent='    ', ensure_ascii=False))

    if generate_index_cardinality_list:
        index_list = list()
        for key, value in index.items():
            temp = [key, len(value)]
            index_list.append(temp)
        index_list.sort(key=lambda x: x[1], reverse=True)
        with open(re.sub('\\.json$', '.txt', output_path), 'w', encoding="utf-8") as outFile:
            for category in index_list:
                outFile.write("%s: %d\n" % (category[0], category[1]))


def categories_from_line(line, category_string):
    """Categories are found at the end of a doc. A series of regex is applied to extract a list of categories.
    category_string is used to pass category tag name, as it is different between different languages."""
    categories_string = re.sub(']].*$', '', line, flags=re.DOTALL)
    categories_string = re.sub(f'^.*\\[\\[{category_string}:\\s*', '', categories_string, flags=re.DOTALL)
    categories_string = to_latin(categories_string)
    return re.compile('\\s*\\|\\s*').split(categories_string)


def load_index(path):
    """Loads index and turns lists it contains into sets. It has to be this way, as sets aren't json serializable."""
    index = json.loads(open(path, 'r', encoding='utf-8').read())
    for category in index:
        index[category] = set(index[category])
    return index
