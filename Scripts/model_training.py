import ktrain
from ktrain import text

from Helpers.dataset import load_dataset_csv
import yaml

# read config
with open(r'../Config/model.yaml', encoding='utf-8') as file:
    config = yaml.full_load(file)

dataset_path = config['dataset-path']
model_name = config['model-name']
val_ratio = config['train-to-val-ratio']
labels = config['labels']
label_count = len(labels)
transformer_max_len = config['transformer-max-len']
learning_rate = config['max-learning-rate']
batch_size = config['learner-batch-size']
epoch_count = config['learner-epoch-count']
model_save_path = config['model-save-path']
estimate_learning_rate_mode = config['estimate-learning-rate-mode']

# load dataset
training_texts, training_labels, validation_texts, validation_labels = \
    load_dataset_csv(dataset_path, val_ratio, label_count)

# choose a model and wrap dataset into ktrain compatible format
transformer = text.Transformer(model_name, maxlen=transformer_max_len, class_names=labels)
train = transformer.preprocess_train(training_texts, training_labels)
validation = transformer.preprocess_test(validation_texts, validation_labels)

# create a learner
model = transformer.get_classifier()
learner = ktrain.get_learner(model, train_data=train, val_data=validation, batch_size=batch_size)

# estimate the learning rate
if estimate_learning_rate_mode:
    print('estimating learning rate. NOT training a model')
    learner.lr_find(show_plot=True, max_epochs=2)
    quit()

# train the model
learner.fit_onecycle(learning_rate, epoch_count)

# create and save the predictor
predictor = ktrain.get_predictor(learner.model, preproc=transformer)
predictor.save(model_save_path)
