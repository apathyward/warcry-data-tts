from data_parsing import FighterJSONPayload, AbilityJSONPayload
import uuid
from pathlib import Path


def generate_id() -> str:
    return str(uuid.uuid4()).split('-')[0]


if __name__ == '__main__':

    payloads = [
        FighterJSONPayload(
            src_file=Path(Path(__file__).parent.parent, 'data', 'fighters.json'),
            schema=Path(Path(__file__).parent.parent, 'data', 'schemas', 'aggregate_fighter_schema.json')
        ),
        AbilityJSONPayload(
            src_file=Path(Path(__file__).parent.parent, 'data', 'abilities.json'),
            schema=Path(Path(__file__).parent.parent, 'data', 'schemas', 'aggregate_ability_schema.json')
        )
    ]

    for p in payloads:
        for entity in p.data:
            if '_id' not in entity.keys() or entity['_id'] in ['PLACEHOLDER', 'XXXXXX']:
                print(f'assigning _id for {entity["name"]}')
                entity['_id'] = generate_id()

        p.write_to_disk()
        print('done')
