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
delete_xml_files = config['delete-xml-files']
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
        print('skipping download of %s as you already have it downloaded' % wiki_local_archives[i])
    elif os.path.exists(wiki_local_xmls[i]):
        print('skipping download of %s as you already have the xml' % wiki_local_archives[i])
    elif os.path.exists(wiki_docs[i]):
        print('skipping download of %s as you already have the docs extracted' % wiki_local_archives[i])
    else:
        print('%s - downloading from %s' % (datetime.now(), wiki_download_urls[i]))
        download(wiki_download_urls[i], wiki_local_archives[i])

# extract wiki files from downloaded archives
for i in range(wiki_count):
    if os.path.exists(wiki_local_xmls[i]):
        print('skipping extraction of %s as you already have the xml' % wiki_local_archives[i])
    elif os.path.exists(wiki_docs[i]):
        print('skipping download of %s as you already have the docs extracted' % wiki_local_archives[i])
    else:
        print('%s - extracting %s' % (datetime.now(), wiki_local_archives[i]))
        extract_bz2(wiki_local_archives[i], wiki_local_xmls[i])

# create and load category indexes
indexes = list()
for i in range(wiki_count):
    if os.path.exists(wiki_indexes[i]):
        print('skipping index generation for %s as it already exists' % wiki_local_xmls[i])
    else:
        print('%s - creating index %s' % (datetime.now(), wiki_indexes[i]))
        create_index(wiki_local_xmls[i], wiki_indexes[i], category_strings[i], generate_index_cardinality_list)
    indexes.append(wiki_indexes[i])
indexes = list(map(lambda index: load_index(index), indexes))

# extract wiki documents from the dumps, doesn't work on Windows
for i in range(wiki_count):
    if os.path.exists(wiki_docs[i]):
        print('skipping doc extraction of %s as %s exists' % (wiki_local_xmls[i], wiki_extracted[i]))
    else:
        print('%s - extracting docs from %s to %s' % (datetime.now(), wiki_local_xmls[i], wiki_extracted[i]))
        extract_docs(wiki_local_xmls[i], wiki_extracted[i])

# remove xml files now that they're processed and too big to leave around. Or don't. You can change that in config.
if delete_xml_files:
    for i in range(wiki_count):
        if os.path.exists(wiki_local_archives[i]) and os.path.exists(wiki_local_xmls[i]):
            print('removing %s since you don\'t need it anymore and still have the .bz2' % wiki_local_xmls[i])
            os.remove(wiki_local_xmls[i])

# create multi-label dataset
if os.path.exists(dataset_path):
    print('dataset %s exists. Delete stuff in %s if you want to repeat related steps' % (dataset_path, working_dir))
else:
    print('%s - creating dataset for labels from %s' % (datetime.now(), label_categories_path))
    create_dataset(indexes, wiki_docs, label_categories_path, dataset_path)

print('%s - done' % datetime.now())
