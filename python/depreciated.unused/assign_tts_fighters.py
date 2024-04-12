import json
import re
import requests
from pathlib import Path
from typing import List, Dict
#this file combines krislings fighters.json from URL and abilities.json file from URL and adds in my local base_sizes.json file to output the tts_fighters.json file.
#this file combines krislings fighters.json from URL and abilities.json file from URL and adds in my local base_sizes.json file to output the tts_fighters.json file.
#this file combines krislings fighters.json from URL and abilities.json file from URL and adds in my local base_sizes.json file to output the tts_fighters.json file.
def normalize(s): 
    return re.sub(r'[^a-z0-9]', '', s.lower())

def assign_abilities(fighters: List[Dict], abilities: List[Dict]) -> List[Dict]:
    for a in abilities:
        faction_match = [x for x in fighters if x['warband'] == a['warband'] or x['bladeborn'] == a['warband']]
        for f in faction_match:
            if set(a['runemarks']).issubset(set(f['runemarks'])):
                f['abilities'].append(a)
    return fighters

def convert_ability_format(fighter: Dict):
    new_abilities = []
    for a in fighter['abilities']:
        if a['warband'] == 'universal':
            continue
        # Capitalize the first letter of the cost value
        new_ability = {'cost': a['cost'].capitalize(), 'name': a['name']}
        new_abilities.append(new_ability)
    # Sort abilities by name to maintain a consistent order
    fighter['abilities'] = sorted(new_abilities, key=lambda x: x['name'])
    return fighter

def add_base_sizes(fighters: List[Dict], base_sizes: List[Dict]):
    for fighter in fighters:
        found = False
        for data_dict in base_sizes:
            for item in data_dict['sheetData']:
                if 'base_size_x' not in item.keys() or 'base_size_y' not in item.keys():
                    continue
                if normalize(fighter['name']) == normalize(item['name']):
                    fighter['base_size_x'] = item['base_size_x']
                    fighter['base_size_y'] = item['base_size_y']
                    found = True
                    break
            if found:
                break
        if not found:
            print('no match found in base sizes for:', fighter['name'])
    return fighters

if __name__ == '__main__':
    fighters_url = 'https://krisling049.github.io/warcry_data/fighters.json'
    abilities_url = 'https://krisling049.github.io/warcry_data/abilities.json'

    response_fighters = requests.get(fighters_url)
    fighters = response_fighters.json()

    response_abilities = requests.get(abilities_url)
    abilities = response_abilities.json()

    base_sizes_path = Path(Path(__file__).parent.parent, 'data', 'baseSizes.json')
    with open(base_sizes_path, 'r') as f:
        base_sizes = json.load(f)

    for f in fighters:
        f['abilities'] = list()

    new_fighters = assign_abilities(fighters, abilities)
    for f in new_fighters:
        convert_ability_format(f)

    new_fighters_with_base_sizes = add_base_sizes(new_fighters, base_sizes)

    output_path = Path(Path(__file__).parent.parent, 'data', 'tts_fighters.json')
    with open(output_path, 'w') as f:
        json.dump(new_fighters_with_base_sizes, f, sort_keys=True, indent=4)
