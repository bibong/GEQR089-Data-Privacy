import pandas as pd
import json
from collections import Counter
import numpy as np

_input_file = 'data/survey.xlsx'
_output_file = 'data/canvas_gl_result.xlsx'
_attribute_list = ['canvas', 'videoCard', 'colorDepth', 'screenResolution']
# _attribute_list = ['fonts', 'languages', 'colorDepth', 'screenResolution', 'timezone', 'sessionStorage', 'localStorage', 'platform', 'plugins', 'canvas', 'vendor', 'cookiesEnabled', 'videoCard']

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
    value_dict = get_value_dict(json_list)
    
    result = {}
    for key, value in value_dict.items():
        result[key] = dict(Counter([convert_to_tuple(v) for v in value]))

    return result

def count_fingerprint(json_list):
    filtered_json_list = []
    for json_obj in json_list:
        filtered_json_obj = {}
        for attribute in _attribute_list:
            tmp = json_obj[attribute]
            if "value" not in tmp:
                tmp = None
            else:
                filtered_json_obj[attribute] = json_obj[attribute]["value"]
        filtered_json_list.append(filtered_json_obj)
    return dict(Counter([convert_to_tuple(json_obj) for json_obj in filtered_json_list]))

def get_value_dict(json_list):
    value_dict = {}
    for json_obj in json_list:
        for key, value in json_obj.items():
            if key not in value_dict:
                value_dict[key] = []
            if "value" not in value:
                value_dict[key].append(None)
            else:
                value_dict[key].append(value["value"])
    
    return value_dict

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

def filter_json_list(json_list):
    ret = []
    for json_obj in json_list:
        if json_obj['platform']['value'] == 'Win32' or json_obj['platform']['value'] == 'MacIntel':
            ret.append(json_obj)

    return ret

def norm_entropy(counter):
    return entropy(counter) / np.log2(np.sum(list(counter.values())))
    
if __name__ == '__main__':
    json_list = read_column(4)
    json_list = filter_json_list(json_list)
    # write_result(count_attribute(json_list))
    write_attribute(count_fingerprint(json_list), 'fingerprint')