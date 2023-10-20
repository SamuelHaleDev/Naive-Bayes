import math
from collections import defaultdict, Counter
import string
import sys

stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]


def main():
    test, train = [], []
    vocabulary, sense, sense_probabilities, conditional_probabilities = defaultdict(Counter), defaultdict(Counter), defaultdict(float), defaultdict(Counter)
    predictions_output = ''
    k = 5
    
    # Get filename from command line
    filename = sys.argv[1]

    # Import data from .wsd file
    data = read_data(filename)

    # Format data
    data = format_data(data)
    data = convert_to_word_instances(data)
    
    fold_generator = k_fold_split(k, data)
    folds = list(fold_generator)

    accuracies = []
    for i in range(k):
        vocabulary, sense, sense_probabilities, conditional_probabilities = defaultdict(Counter), defaultdict(Counter), defaultdict(float), defaultdict(Counter)
        
        test = folds[i]
        train = [fold for j, fold in enumerate(folds) if j != i]

        # Grab counts for vocabulary and sense
        vocabulary, sense = initialize_vocabulary_and_sense(train, vocabulary, sense)

        # Grab prior and conditional probabilities
        sense_probabilities = calculate_prior_probabilities(train, sense, sense_probabilities)
        conditional_probabilities = precalculate_conditional_probabilities(vocabulary, sense, conditional_probabilities)

        # Make Predictions
        fold_predictions = {}
        for instance in test:
            fold_predictions[instance.instance_id] = naive_bayes_predict(instance, sense, sense_probabilities, conditional_probabilities, vocabulary)

        # Write fold predictions to predictions_output
        predictions_output += "Fold " + str(i+1) + ":\n"
        for instance_id in fold_predictions:
            predictions_output += instance_id + " " + fold_predictions[instance_id] + "\n"
            
        fold_accuracy = calculate_accuracies(fold_predictions, test)
        print("Fold " + str(i+1) + " accuracy: ", fold_accuracy)
        accuracies.append(fold_accuracy)

    mean_accuracy = sum(accuracies) / len(accuracies)
    print("Mean accuracy: ", mean_accuracy)
    
    # Write predictions_output to plant.wsd.out
    with open(f"{filename}.out", 'w') as f:
        f.write(predictions_output)
        
        
def naive_bayes_predict(instance, sense, sense_probability, conditional_probability, vocabulary):
    probabilities = {}
    for sense_type in sense:
        probability = math.log2(sense_probability[sense_type])
        for feature in instance.features:
            if conditional_probability[feature][sense_type] != 0:
                probability += math.log2(conditional_probability[feature][sense_type])
            else:
                probability += math.log2(1 / (sum(sense[sense_type].values()) + len(vocabulary)))
        probabilities[sense_type] = probability
    predicted_sense = max(probabilities, key=probabilities.get)
    return predicted_sense

       
class WordInstance:
    def __init__ (self, instance_id, sense_id, context, head):
        self.instance_id = instance_id
        self.sense_id = sense_id
        self.context = context
        self.head = head
        self.features = []

    def extract_features(self):
        global stop_words
        tokens = self.context.split()
        for token in tokens:
            if token not in string.punctuation and token.lower() not in stop_words:
                token = token.rstrip(string.punctuation)
                self.features.append(token)
       
                
def convert_to_word_instances(data):
    list_instances = []
    for instance in data:
        for i, line in enumerate(instance):
            if line.startswith('<instance'):
                instance_id = line.split('"')[1]
            elif line.startswith('<answer'):
                sense_id = line.split('"')[3]
            elif line.startswith('<context>'):
                context = instance[i+1].replace('\n', ' ')
                head = context.split('<head>')[1].split('</head>')[0]
                context = context.replace(' <head>' + head + '</head> ', '')
        word_instance = WordInstance(instance_id, sense_id, context, head)
        word_instance.extract_features()
        list_instances.append(word_instance)
    return list_instances


def read_data(file_name):
    with open(file_name, 'r') as f:
        data = f.readlines()
    return data


def format_data(data):
    formatted_data = []
    temp_line = []
    for line in data:
        if line != '\n':
            temp_line.append(line)
        else:
            if temp_line != []:
                formatted_data.append(temp_line)
            temp_line = []
    return formatted_data
    
    
def k_fold_split(k, data):
    size = len(data) // k
    for i in range(0, len(data), size):
        yield data[i:i + size]
      
        
def initialize_vocabulary_and_sense(data, vocabulary, sense):
    for fold in data:
        for instance in fold:
            for feature in instance.features:
                vocabulary[feature][instance.sense_id] += 1
                sense[instance.sense_id][feature] += 1
    return vocabulary, sense


def calculate_prior_probabilities(data, sense, sense_probability):
    sense_instance = defaultdict(int)
    data_length = 0
    for fold in data:
        for instance in fold:
            sense_instance[instance.sense_id] += 1
            data_length += 1
    for sense_type in sense:
        sense_probability[sense_type] = sense_instance[sense_type] / data_length
    return sense_probability


def calculate_conditional_probabilities(vocabulary, word, sense, sense_type):
    return (vocabulary[word][sense_type] + 1)/(sum(sense[sense_type].values()) + len(vocabulary))


def precalculate_conditional_probabilities(vocabulary, sense, conditional_probability):
    for word in vocabulary:
        for sense_type in sense:
            conditional_probability[word][sense_type] = calculate_conditional_probabilities(vocabulary, word, sense, sense_type)
    return conditional_probability


def calculate_accuracies(predictions, data):
    correct = 0
    for instance in data:
        if instance.sense_id == predictions[instance.instance_id]:
            correct += 1
    accuracy = correct / len(data)
    return accuracy

main()