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