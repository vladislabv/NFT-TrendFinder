import random
from helpers.add_extensions import find_nth

def prepare_data(dashboard_data):

    for i in dashboard_data:
        if i[1] == 'rich_pairs':
            rich_items_data = i[0]
        elif i[1] == 'value_aggregation':
            top_values = i[0]
        elif i[1] == 'key_aggregation':
            top_keys = i[0]
        elif i[1] == 'pair_aggregation':
            top_pairs_data = i[0]
        else:
            raise Exception("The route handler has got a unknown agggregation_pipeline")

    rich_pairs = list(
        map(
            lambda x: str(x['_id']['price']) + ' ' + 'ETH: ' + ', '.join(x['pairs'])[:find_nth(', '.join(x['pairs']), ',', 10)], rich_items_data
        )
    )
    rich_images = list(
        map(
            lambda x: x['_id']['filename'].split('/')[-1], rich_items_data
        )
    )
    rich_info = list(
        map(
            lambda x: 'name: ' + x['_id'].get('name', 'Currently the name is not available.') + '\n' + 'price: ' + str(x['_id']['price']), rich_items_data
        )
    )
    top_pairs = list( 
        map(lambda x: x['_id'] + ' ' + str(x['totalAmount']), top_pairs_data)
    )

    rich_images_with_info = enumerate(zip(rich_images, rich_info))

    # schuffle lists before looping
    random.shuffle(top_values)
    random.shuffle(top_keys)
    generated_pairs = []
    for new_pair in zip(top_values, top_keys):
        new_pair = new_pair[0]['_id'] + ' ' + new_pair[1]['_id']
        generated_pairs.append(new_pair)

    return {
        'top_pairs': top_pairs, 
        'generated_pairs': generated_pairs, 
        'rich_pairs': rich_pairs, 
        'rich_images_with_info': rich_images_with_info
    }