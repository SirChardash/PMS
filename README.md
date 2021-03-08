# Summary
This project contains python scripts that utilize ktrain, tensorflow and BERT to train multi-label classification on serbian texts. I say serbian, but it really runs
on croatian as cyrillic/latin are probably defining factors of language detection for these languages. Training texts are retrieved from wikipedia dumps for serbian
and croatian language, then thrown through the processing pipeline to form ktrain-compatible dataset. When playing around, you probably want to tinker with `Config/*`
files first. All of parameters are extracted there.

# What you need
* python 3.6 (tensorflow doesn't currently work with 3.7)
* CUDA Runtime (11.1 is a safe bet, I don't think latest version works wit tensorflow yet)
* install requirements from `requirements.txt` (see comment in the file if tensorflow fails because of setuptools)

# How to run
* either navigate to Scripts dir to run scripts, or modify loading/safe paths in `Config/*` files to have a reasonable directory structure
* run `prepare_dataset.py` (expect it to run for 1-2h, but see the bottom of the document first). It will
  * download and extract wiki files
  * go through extracted xml files and create a category index. It will provide mapping from doc id to categories it belongs to
  * run wikiextractor (only part that doesn't work on Windows) to remove wiki syntax, allowing for simpler doc content reading
    * it will create `wikiname/AA/wiki_numbers` files, which you can inspect with text editor to get familiar
  * create a multi-label dataset from wiki files, indexes and `Data/categories.json` file
    * `Data/categories.json` file contains a mapping from classifying labels that we will use to wiki categories that belong to it
    * `Data/categories.json` file and `Config/model.yaml#labels` field are the only thing here that decide that we're classifying biology texts
* check `Config/model.yaml`
  * you probably want to start with `estimate-learning-rate-mode` set to yes instead of training right away
    * this is value is dependent on the dataset. As I've done it for the dataset generated, you don't need to do this if you don't do anything to change the dataset
    * it will run two iterations of training rate and help you decide optimal `max-learning-rate`
    * when you run `model_training.py` with this flag, you'll get a graph. Choose `max-learning-rate` using elbow rule
      * find the learning rate value that gives minimal loss rate
      * find that there is a slope going to that spot from left to right
      * choose the value on the middle of a slope
      * that somewhat gives the best rate that will find the minimal loss rate spot (it will probably be close to 10^-5)
    * update `transformer-max-len` and `learner-batch-size` to get best results and performance for your hardware environment
      * set `transformer-max-len` higher to get better representation of documents (where 500 seems to be the highest you need to go, internet says)
      * match `learner-batch-size` to increase performance. Choose the highest value that doesn't break `model_training.py` due to low GPU memory
    * play around with `learner-epoch-count`. 4 is a great starting point
* run `model_training.py`
* run `demonstration.py` and open `Gui/gui.html`

## if prepare_dataset is too much
You can download the model [here](https://drive.google.com/file/d/1kmMtPtZpdhRxlZ17teeVAQCBmbz-sy97/view). I guess it's best to test the model first, then dive into
implementation.
