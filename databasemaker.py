import os
import urllib.request
import json 
from collections import defaultdict

class DatabaseMaker():
    def __init__(self, school_name, major_code, id_to_key): #defined parameters, the constructor method
        self.database = defaultdict(list)
        with urllib.request.urlopen("https://assist.org/api/institutions") as url: #connects to the url and allows for data to be read, the url connection is closed once fully iterated.
            data = json.loads(url.read().decode()) #url.read reads the data in bytes, .decode allows the data to be converted to strings. All of this data is then stored into data
        self.names = {x['id']: x['names'][0]['name'] for x in list(data)} #as JSON shares similar data types, some of these may be dictionary data types.
        self.major_code = major_code
        self.school_name = school_name
        self.id_to_key = id_to_key
        
    def alphabetize_class_dict(self, class_dict): #
        sorted_classes = sorted(class_dict.keys())
        class_dict = {key: class_dict[key] for key in sorted_classes}
        for key in class_dict.keys(): #iterates through every key (such as 'from_school') that is contained within the class (seen in add_classes)
            sorted_schools = sorted(class_dict[key], key=lambda x : x['from_school']) #sorts only the 'from_school' of x, a dictionary data type, 
            class_dict[key] = sorted_schools
        return class_dict
    
    def add_classes(self):
        for file_name in os.listdir('agreements/'): #iterates through each file within the directory of 'agreements/'
            if self.major_code not in file_name or 'report' not in file_name:
                continue
            info = file_name.replace('.pdf', '').split('_') #splits the name of the file (containing the school id) 
            #each file name will contain the school ids of the "from" and the "to" schools
            to_school_id = info[1] #
            from_school_id = int(info[2]) 
            extractor = PDF_Extractor(f'agreements/{file_name}')
            classes = extractor.dict_from_file()
            for to_class in classes.keys():
                from_class = {'school_id': from_school_id,
                              'from_school': self.names[from_school_id],
                              'equiv': classes[to_class],
                              'key': id_to_key[from_school_id]}
                self.database[to_class].append(from_class)
        self.database = self.alphabetize_class_dict(self.database)
        json_name = f'agreements/{self.school_name}/{self.major_code}.json'
        with open(json_name, "w") as out_file: 
            json.dump(self.database, out_file, indent=4)
