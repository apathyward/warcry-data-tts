import requests
import re
import os
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

    if isinstance(abilities, dict):
        iterable = abilities.items()
    elif isinstance(abilities, list):
        iterable = enumerate(abilities)
    else:
        raise ValueError("Expected a dict or list for abilities")

    for ability_id, ability_details in iterable:
        inner_spaces = '   ' * (indent + 1)
        ability_lua = '{\n' + ',\n'.join(
            [inner_spaces + (f'{k}="{v}"' if isinstance(v, str) else f'{k}={custom_serialize(v, indent + 1)}') 
             for k, v in ability_details.items()]
        ) + '\n' + spaces + '}'
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
    description = re.sub(r'([0-9A-Za-z])"', r'\1\\"', description)
    # Replace newline characters with Lua newline escape sequence
    description = description.replace('\n', '\\n')
    return description

def add_backslashes_to_abilities(abilities: List[Dict]) -> List[Dict]:
    for ability in abilities:
        if 'description' in ability:
            # First remove specific quotes
            ability['description'] = remove_specific_inner_double_quotes(ability['description'])
            # Then escape all remaining inches/quotes
            ability['description'] = add_backslashes_to_inches(ability['description'])
    return abilities

def remove_newlines(lua_string):
    # Remove all newline characters from the string
    return lua_string.replace("\n", "")

def remove_specific_inner_double_quotes(description: str) -> str:
    # Remove double quotes only around Wall Run (exact match)
    return re.sub(r'"Wall Run"', 'Wall Run', description)

def download_file(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for failed requests
    return response.json()  # Assuming JSON content

if __name__ == '__main__':
    print("Script started.")
    try:
        # Get the current script directory and target the lua folder
        script_dir = Path(__file__).parent  # The directory where this script is located
        lua_dir = script_dir.parent / "lua"  # Move up one level to root and then into lua
        lua_dir.mkdir(parents=True, exist_ok=True)  # Ensure the folder exists

        # Raw GitHub URLs
        fighters_url = 'https://raw.githubusercontent.com/krisling049/warcry_data/refs/heads/main/docs/fighters_tts.json'
        base_sizes_url = 'https://raw.githubusercontent.com/apathyward/warcry-data-tts/main/data/baseSizes.json'
        abilities_url = 'https://raw.githubusercontent.com/krisling049/warcry_data/refs/heads/main/docs/abilities.json'

        # Download the data from GitHub
        fighters = download_file(fighters_url)
        base_sizes = download_file(base_sizes_url)
        abilities = download_file(abilities_url)

        # Process fighters and base sizes
        fighters = fix_special_characters_in_names(fighters)
        fighters_with_base_sizes = add_base_sizes(fighters, base_sizes)

        # Apply backslashes to inch symbols in ability descriptions
        abilities = add_backslashes_to_abilities(abilities)

        # Serialize to Lua format
        fighters_lua_content = "return " + custom_serialize(fighters_with_base_sizes)
        abilities_lua_content = "return " + serialize_ability_without_parent_key(abilities)

        # Write abilities data to lua/abilities_test.lua
        with open(lua_dir / 'abilities_test.lua', 'w') as f:
            f.write(abilities_lua_content)

        # Write fighters data to lua/fighters_test.lua
        with open(lua_dir / 'fighters_test.lua', 'w') as f:
            f.write(fighters_lua_content)

        print("Script executed successfully. Files saved in the 'lua' folder.")
    except Exception as e:
        print(f"An error occurred: {e}")
