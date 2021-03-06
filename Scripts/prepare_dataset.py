from datetime import datetime
import os
from pathlib import Path
import re

import yaml

from Helpers.dataset import create_dataset
from Helpers.index import create_index, load_index
from Helpers.wiki_prep import extract_docs, extract_bz2, download

# read config and calculate paths to use. Keep in mind that I put WorkingData dir one level above running dir, so it's
# best to run these scripts from their parent directory, or change the working dir in Config/dataset.yaml.
with open(r'../Config/dataset.yaml', encoding='utf-8') as file:
    config = yaml.full_load(file)

category_strings = config['category-strings']
generate_index_cardinality_list = config['generate-index-cardinality-list']
label_categories_path = config['label-categories-path']

working_dir = config['working-dir']
dataset_path = working_dir + config['dataset-path']
wiki_download_urls = config['wiki-download-urls']
wiki_local_archives = list(map(lambda url: working_dir + re.sub('^.*/', '', url), wiki_download_urls))
wiki_local_xmls = list(map(lambda url: re.sub('\\.bz2$', '', url), wiki_local_archives))
wiki_extracted = list(map(lambda url: re.sub('-.*$', '', url), wiki_local_xmls))
wiki_docs = list(map(lambda url: url + '/AA', wiki_extracted))
wiki_indexes = list(map(lambda url: url + '-index.json', wiki_extracted))
wiki_count = len(wiki_download_urls)

# create working dir
Path(working_dir).mkdir(exist_ok=True)

# download wiki files
for i in range(wiki_count):
    if os.path.exists(wiki_local_archives[i]):
        print(f'skipping download of {wiki_local_archives[i]} as you already have it downloaded')
    elif os.path.exists(wiki_local_xmls[i]):
        print(f'skipping download of {wiki_local_archives[i]} as you already have the xml')
    elif os.path.exists(wiki_docs[i]):
        print(f'skipping download of {wiki_local_archives[i]} as you already have the docs extracted')
    else:
        print(f'{datetime.now()} - downloading from {wiki_download_urls[i]}')
        download(wiki_download_urls[i], wiki_local_archives[i])

# extract wiki files from downloaded archives
for i in range(wiki_count):
    if os.path.exists(wiki_local_xmls[i]):
        print(f'skipping extraction of {wiki_local_archives[i]} as you already have the xml')
    elif os.path.exists(wiki_docs[i]):
        print(f'skipping download of {wiki_local_archives[i]} as you already have the docs extracted')
    else:
        print(f'{datetime.now()} - extracting {wiki_local_archives[i]}')
        extract_bz2(wiki_local_archives[i], wiki_local_xmls[i])

# create and load category indexes
indexes = list()
for i in range(wiki_count):
    if os.path.exists(wiki_indexes[i]):
        print(f'skipping index generation for {wiki_local_xmls[i]} as it already exists')
    else:
        print(f'{datetime.now()} - creating index {wiki_indexes[i]}')
        create_index(wiki_local_xmls[i], wiki_indexes[i], category_strings[i], generate_index_cardinality_list)
    indexes.append(wiki_indexes[i])
indexes = list(map(lambda index: load_index(index), indexes))

# extract wiki documents from the dumps, doesn't work on Windows
for i in range(wiki_count):
    if os.path.exists(wiki_docs[i]):
        print(f'skipping doc extraction of {wiki_local_xmls[i]} as {wiki_extracted[i]} exists')
    else:
        print(f'{datetime.now()} - extracting docs from {wiki_local_xmls[i]} to {wiki_extracted[i]}')
        extract_docs(wiki_local_xmls[i], wiki_extracted[i])

# notify that big files aren't needed anymore
for i in range(wiki_count):
    if os.path.exists(wiki_local_archives[i]) and os.path.exists(wiki_local_xmls[i]):
        print(f'it\'s safe to delete {wiki_local_xmls[i]} since you don\'t need it anymore and still have the .bz2')

# create multi-label dataset
if os.path.exists(dataset_path):
    print(f'dataset {dataset_path} exists. Delete stuff in {working_dir} if you want to repeat related steps')
else:
    print(f'{datetime.now()} - creating dataset for labels from {label_categories_path}')
    create_dataset(indexes, wiki_docs, label_categories_path, dataset_path)

print(f'{datetime.now()} - done')
