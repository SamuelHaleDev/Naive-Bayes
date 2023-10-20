import math
from collections import defaultdict, Counter
import string
# To Do:
# 4. Build model training function
# 5. Build prediction and evaluation function
# 6. Build main function
# 7. Build output file 
def main():
    test = []
    train = []
    vocabulary = defaultdict(Counter)
    
    # Import data from .wsd file
    data = read_data("plant.wsd")
    
    # Format data
    data = format_data(data)
    
    data = convert_to_word_instances(data)
    
    fold_generator = k_fold_split(5, data)
    
    for i, fold in enumerate(fold_generator):
        if i == 0:
            test.append(fold)
        else:
            train.append(fold)
            vocabulary = initialize_vocabulary(fold, vocabulary)
            
    
            
class WordInstance:
    def __init__ (self, instance_id, sense_id, context, head):
        self.instance_id = instance_id
        self.sense_id = sense_id
        self.context = context
        self.head = head
        self.features = []

    def extract_features(self):
        tokens = self.context.split()
        for token in tokens:
            if token not in string.punctuation:
                self.features.append(token.lower())
                
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
        
def initialize_vocabulary(fold, vocabulary):
    for instance in fold:
        for feature in instance.features:
            vocabulary[feature][instance.sense_id] += 1
    return vocabulary
    
main()