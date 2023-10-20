# To Do:
# 1. Import data from .wsd file
# 2. Build k-fold cross validation function
# 3. Build feature extraction function
# 4. Build model training function
# 5. Build prediction and evaluation function
# 6. Build main function
# 7. Build output file 
def main():
    test = []
    train = []
    
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
            
class WordInstance:
    def __init__ (self, instance_id, sense_id, context, head):
        self.instance_id = instance_id
        self.sense_id = sense_id
        self.context = context
        self.head = head
        self.features = []
        
    def extract_features(self):
        tokens = self.context.split()
        self.features = [(tokens[i], tokens[i+1]) for i in range(len(tokens)-1)]
            
def convert_to_word_instances(data):
    #['<instance id="plant.1000000" docsrc = "BNC/A07">\n', '<answer instance="plant.1000000" senseid="plant%factory"/>\n', '<context>\n', 'Until the mid- and late 1970s, there were simply no rules whereby groupings of parents could obtain a state-financed, multi-denominational school, as the only channels of communication in these matters were those between the Department of Education and the relevant diocesan department or other church board. For example, a new housing estate would be built, the diocese would be informed of the development at the planning stage, and the diocesan office would put in for a school, or an extension for an existing school. The arrangement had been unchanged since the early years of the state and had become entirely natural. Similarly for the protestant community: the school  <head>plant</head>  is owned by the church, or appropriate church body. \n', '</context>\n', '</instance>\n']
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
    
main()