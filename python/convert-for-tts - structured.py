import json
import re
import requests
from pathlib import Path
from typing import List, Dict

def normalize(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', s.lower())

def add_base_sizes(fighters: List[Dict], base_sizes: Dict) -> List[Dict]:
    for fighter in fighters:
        found = False
        for faction, entities in base_sizes.items():
            for entity in entities:
                if 'base_size_x' not in entity or 'base_size_y' not in entity:
                    continue
                if normalize(fighter['name']) == normalize(entity['name']):
                    fighter['base_size_x'] = entity['base_size_x']
                    fighter['base_size_y'] = entity['base_size_y']
                    found = True
                    break
            if found:
                break
        if not found:
            print(f"No match found in base sizes for: {fighter['name']}")
    print("Base sizes successfully added to all applicable fighters.")
    return fighters

def capitalize_ability_costs(fighters: List[Dict]) -> List[Dict]:
    for fighter in fighters:
        if 'abilities' in fighter:
            for ability in fighter['abilities'].values():
                ability['cost'] = ability['cost'].capitalize()
    print("Ability costs capitalized for all fighters.")
    return fighters

def serialize_ability_without_parent_key(abilities: Dict, indent=0) -> str:
    spaces = '   ' * indent
    abilities_lua = []
    for ability_id, ability_details in abilities.items():
        inner_spaces = '   ' * (indent + 1)
        ability_lua = '{\n' + ',\n'.join([inner_spaces + (f'{k}="{v}"' if isinstance(v, str) else f'{k}={custom_serialize(v, indent + 1)}') for k, v in ability_details.items()]) + '\n' + spaces + '}'
        abilities_lua.append(ability_lua)
    return '{\n' + ',\n'.join(abilities_lua) + '\n}'

def custom_serialize(var, indent=0) -> str:
    spaces = '   ' * indent
    if isinstance(var, (list, tuple)):
        inner_spaces = '   ' * (indent + 1)
        result = '{\n' + ',\n'.join([inner_spaces + custom_serialize(x, indent + 1) for x in var]) + '\n' + spaces + '}'
    elif isinstance(var, dict):
        inner_spaces = '   ' * (indent + 1)
        result = '{\n' + ',\n'.join([inner_spaces + (f'["{k}"]=' if not k.isidentifier() else f'{k}=') + custom_serialize(v, indent + 1) for k, v in var.items()]) + '\n' + spaces + '}'
    elif isinstance(var, str):
        escaped_var = var.replace('\n', '').replace('"', '\\"')
        result = f'"{escaped_var}"'
    else:
        result = f'"{str(var)}"'
    return result

def fix_special_characters_in_names(fighters: List[Dict]) -> List[Dict]:
    for fighter in fighters:
        if fighter['_id'] == '6bb3286e':
            fighter['name'] = 'Witch Aelf with Paired Sciansa'
        elif fighter['_id'] == '1aeda80d':
            fighter['name'] = 'Witch Aelf with Sciansa and Bladed Buckler'
    print("Finished fixing special characters in fighter names.")
    return fighters

def add_backslashes_to_inches(description: str) -> str:
    # Add backslashes before inches
    description = re.sub(r'(\d)"', r'\1\\"', description)
    # Replace newline characters with Lua newline escape sequence
    description = description.replace('\n', '\\n')
    return description

def remove_newlines(lua_string):
    # Remove all newline characters from the string
    return lua_string.replace("\n", "")

def remove_specific_inner_double_quotes(description: str) -> str:
    # Targeted removal of double quotes around specific words like "Wall Run"
    return re.sub(r'"(Wall Run)"', r'\1', description)

if __name__ == '__main__':
    print("Script started.")
    try:
        fighters_url = 'https://krisling049.github.io/warcry_data/fighters_tts.json'
        response_fighters = requests.get(fighters_url)
        fighters = response_fighters.json()

        fighters = fix_special_characters_in_names(fighters)

        base_sizes_path = Path('C:/Users/mabea/Documents/ALL WARCRY/warcry-data-tts/data', 'baseSizes.json')
        with open(base_sizes_path, 'r') as f:
            base_sizes = json.load(f)

        fighters_with_base_sizes = add_base_sizes(fighters, base_sizes)

        output_path = Path('C:/Users/mabea/Documents/ALL WARCRY/warcry-data-tts/data', 'tts_fighters.json')
        with open(output_path, 'w') as f:
            json.dump(fighters_with_base_sizes, f, sort_keys=True, indent=4)

        abilities_url = 'https://krisling049.github.io/warcry_data/abilities.json'
        response_abilities = requests.get(abilities_url)
        abilities = response_abilities.json()

        # Apply modifications to abilities descriptions
        for ability in abilities:
            if 'description' in ability:
                ability['description'] = add_backslashes_to_inches(ability['description'])
                ability['description'] = remove_specific_inner_double_quotes(ability['description'])

        abilities_key_value_table = {item['_id']: item for item in abilities}

        abilities_lua_content = "return " + serialize_ability_without_parent_key(abilities_key_value_table)

        abilities_lua_path = Path('C:/Users/mabea/Documents/ALL WARCRY/warcry-data-tts/lua', 'abilities.lua')
        with open(abilities_lua_path, 'w', encoding='utf-8') as lua_file:
            lua_file.write(abilities_lua_content)

        fighters_lua_path = Path('C:/Users/mabea/Documents/ALL WARCRY/warcry-data-tts/lua', 'fighters.lua')
        with open(fighters_lua_path, 'w', encoding='utf-8') as lua_file:
            lua_file.write("return " + custom_serialize(fighters_with_base_sizes))

        print("Script executed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
