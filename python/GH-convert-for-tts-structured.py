def add_backslashes_to_abilities(abilities: List[Dict]) -> List[Dict]:
    for ability in abilities:
        if 'description' in ability:
            ability['description'] = add_backslashes_to_inches(ability['description'])
    return abilities

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
