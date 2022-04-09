"""The file fetches data from Rarible API and saves it to the local MongoDB Database"""

from definitions_of_classes import OutputAPI
from definitions_of_classes import MongoDB


def main():
    result_status = 0
    try:
        items_df = OutputAPI(duration=5)
        items_df = items_df.fetch_items_from_API()
        items_df.to_csv('output_df.csv', index=False, encoding='utf-8')
    except Exception as e:
        print(e)
        result_status = 1
    db = MongoDB.get_database()
    print(db)
    return result_status


if __name__ == '__main__':
    finished_status = main()
    print(f'The program ended with the status {finished_status}.')
    if finished_status:
        print('Script has been successfully executed! All data are saved under "output_df.csv".')
    else:
        print('Oops! Something has gone not smoothly, the output could not be created.')
