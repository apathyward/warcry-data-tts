import json
import requests
import re

def normalize(s): 
   return re.sub(r'[^a-z0-9]', '', s.lower())

# Use the new URL here
response_a = requests.get('https://raw.githubusercontent.com/apathyward/warcry-data-jr/main/data/tts_fighters.json')
data_a = response_a.json()

response_b = requests.get('https://raw.githubusercontent.com/apathyward/warcry-data-jr/main/data/baseSizes.json')
data_b = response_b.json()

output = data_a.copy()

for item_a in output:
   found = False # flag to check if a match was found
   for data_dict in data_b: # iterate over the dictionaries in data_b
       for item_b in data_dict['sheetData']: # iterate over the items in sheetData
           if 'base_size_x' not in item_b.keys() or 'base_size_y' not in item_b.keys():
               continue

           if normalize(item_a['name']) == normalize(item_b['name']):
               # insert the base_size_x and base_size_y keys and values
               item_a['base_size_x'] = item_b['base_size_x']
               item_a['base_size_y'] = item_b['base_size_y']
               found = True # a match was found
               break
       if found: # if a match was found, break the outer loop
           break
   if not found: # if no match was found, print the name value
       print('no match found in file b for:', item_a['name'])

for item_a in output:
   if 'base_size_x' not in item_a.keys() or 'base_size_y' not in item_a.keys():
       print('no base_size_x or base_size_y found in output for:', item_a['name'])

with open('c:/users/mabea\documents/all warcry/warcry-data-jr/data/tts_fighters_abilities_base_sizes.json', 'w') as f: 
   json.dump(output, f)
