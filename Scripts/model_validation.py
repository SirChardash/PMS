import ktrain
import yaml

from Helpers.dataset import load_dataset_csv

with open(r'../Config/model.yaml', encoding='utf-8') as file:
    config = yaml.full_load(file)

dataset_path = config['dataset-path']
val_ratio = config['train-to-val-ratio']
labels = config['labels']
label_count = len(labels)

predictor = ktrain.load_predictor(config['model-save-path'])
_, _, validation_texts, validation_labels_array = load_dataset_csv(dataset_path, val_ratio, label_count)
validation_labels = []

for labels_array in validation_labels_array:
    labels_set = set()
    for i in range(len(labels_array)):
        if labels_array[i]:
            labels_set.add(labels[i])
    validation_labels.append(labels_set)

print('validating on %d texts' % len(validation_texts))

true_positives = dict()
false_positives = dict()
false_negatives = dict()

for label in labels:
    true_positives[label] = 0
    false_positives[label] = 0
    false_negatives[label] = 0

for i in range(len(validation_texts)):
    if i != 0:
        if i % 1000 == 0:
            print('○', end=' ', flush=True)
        elif i % 100 == 0:
            print('•', end=' ', flush=True)
    for prediction in predictor.predict(validation_texts[i]):
        if prediction[1] < 0.5 and prediction[0] in validation_labels[i]:
            false_negatives[prediction[0]] = false_negatives[prediction[0]] + 1
        if prediction[1] > 0.5:
            if prediction[0] in validation_labels[i]:
                true_positives[prediction[0]] = true_positives[prediction[0]] + 1
            else:
                false_positives[prediction[0]] = false_positives[prediction[0]] + 1

print()
print('true positives: %s' % true_positives)
print('false positives: %s' % false_positives)
print('false negatives: %s' % false_negatives)

for label in labels:
    print('P(%s) \t= %.5f' % (label, true_positives[label] / (true_positives[label] + false_positives[label])))
    print('R(%s) \t= %.5f' % (label, true_positives[label] / (true_positives[label] + false_negatives[label])))

pTotal = sum(true_positives.values()) / (sum(true_positives.values()) + sum(false_positives.values()))
rTotal = sum(true_positives.values()) / (sum(true_positives.values()) + sum(false_negatives.values()))
print('P(total) \t= %.5f' % pTotal)
print('R(total) \t= %.5f' % rTotal)
