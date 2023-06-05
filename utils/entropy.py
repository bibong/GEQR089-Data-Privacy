import pandas as pd
import json
from collections import Counter
import numpy as np

_input_file = '../data/survey.xlsx'
_output_file = '../data/result.xlsx'
_attribute_list = []

def read_column(nth):
    data_frame = pd.read_excel(_input_file)
    json_column = data_frame.iloc[:, nth]
    json_list = []

    for json_str in json_column:
        json_obj = json.loads(json_str)
        json_list.append(json_obj)

    return json_list

def write_attribute(counter, sheet_name):
    data = {'fingerprint': [], 'count': []}

    for key, value in counter.items():
        data['fingerprint'].append(key)
        data['count'].append(value)

    data['entropy'] = entropy(counter)
    data['normalized entropy'] = norm_entropy(counter)

    data_frame = pd.DataFrame(data)
    with pd.ExcelWriter(_output_file, mode='a', engine='openpyxl') as writer:
        data_frame.to_excel(writer, sheet_name=sheet_name, index=False)

def write_result(result):
    for attribute, counter in result.items():
        write_attribute(counter, attribute)

def count_attribute(json_list):
    value_dict = {}
    for json_obj in json_list:
        for key, value in json_obj.items():
            if key not in value_dict:
                value_dict[key] = []
            if "value" not in value:
                value_dict[key].append(None)
            else:
                value_dict[key].append(value["value"])
    
    result = {}
    for key, value in value_dict.items():
        result[key] = dict(Counter([convert_to_tuple(v) for v in value]))

    return result

def count_fingerprint(json_list):
    # if str not in _attribute_list
    # del json[str]
    return dict(Counter([convert_to_tuple(json_obj) for json_obj in json_list]))

def convert_to_tuple(element):
    if isinstance(element, dict):
        return tuple((k, convert_to_tuple(v)) for k, v in element.items())
    elif isinstance(element, list):
        return tuple(convert_to_tuple(e) for e in element)
    else:
        return element
    
def entropy(counter):
    result = 0.0
    sum = np.sum(list(counter.values()))
    for key, value in counter.items():
        prob = value / sum
        result += -prob * np.log2(prob)

    return result

def norm_entropy(counter):
    return entropy(counter) / np.sum(list(counter.values()))
    
if __name__ == '__main__':
    json_list = read_column(4)
    write_result(count_attribute(json_list))
    write_attribute(count_fingerprint(json_list), 'fingerprint')