import json
import urllib.request
#this converts my local tts_fighters.json & krislings abilities.json URL to separate lua files.
#this converts my local tts_fighters.json & krislings abilities.json URL to separate lua files.
#this converts my local tts_fighters.json & krislings abilities.json URL to separate lua files.
# Custom serialize function to generate LUA syntax with all values as strings
def custom_serialize(var, parent_key=None):
    keys_to_quote = ["grand_alliance", "dmg_crit", "dmg_hit", "max_range", "min_range", "base_size_x", "base_size_y"]
    if isinstance(var, (list, tuple)):
        return '{' + ', '.join([custom_serialize(x) for x in var]) + '}'
    elif isinstance(var, dict):
        return '{' + ', '.join([f'["{k}"]=' + custom_serialize(v, k) if k in keys_to_quote or not k.isidentifier() else f'{k}=' + custom_serialize(v, k) for k, v in var.items()]) + '}'
    elif isinstance(var, str):
        escaped_var = var.replace('\n', '').replace('"', '\\"')
        return f'"{escaped_var}"'
    else:
        # Convert all non-string values to strings and quote them
        return f'"{str(var)}"'

# Load and process fighters data from local file
json_file_path = r'C:/Users/mabea/Documents/ALL WARCRY/warcry-data-jr/data/tts_fighters.json'
with open(json_file_path, 'r', encoding='utf-8') as file:
    fighters_data = json.load(file)

fighters_key_value_table = {}
for item in fighters_data:
    key = item['name']
    value = {k: v for k, v in item.items() if k != '_id'}
    fighters_key_value_table[key] = value

fighters_file_path = r'C:/Users/mabea/Documents/ALL WARCRY/warcry-data-jr/lua/fighters.lua'
with open(fighters_file_path, 'w', encoding='utf-8') as lua_file:
    lua_file.write("return " + custom_serialize(fighters_key_value_table))

# Load and process abilities data from URL
json_url = 'https://krisling049.github.io/warcry_data/abilities.json'
response = urllib.request.urlopen(json_url)
abilities_data = json.loads(response.read().decode('utf-8'))

abilities_key_value_table = {}
for item in abilities_data:
    key = item['name']
    value = {k: v for k, v in item.items() if k not in ('_id', 'warband', 'runemarks')}
    abilities_key_value_table[key] = value

abilities_file_path = 'C:/Users/mabea/Documents/ALL WARCRY/warcry-data-jr/lua/abilities.lua'
with open(abilities_file_path, 'w', encoding='utf-8') as lua_file:
    lua_file.write("return " + custom_serialize(abilities_key_value_table))
