import boto3
import datetime

TRAIN_LINES = [
    '123',
    '456',
    '7',
    'ACE',
    'BDFM',
    'G',
    'JZ',
    'L',
    'NQR',
    'S',
    'SIR',
]


def _normalize_dynamo_response(response):
    """
    Flatten DynamoDB's response from a list of dicts to a structure that's
    easier to work with:
    ```
    { 'TRAIN_LINE':
        { 'date': $DATE,
          'status_title': $STATUS_TITLE,
          'is_it_fucked': $IS_IT_FUCKED }
     }
    ```

    Which makes querying in python easier:
    ```
    response.get('NQR').get('is_it_fucked')
    ```
    """
    normalized_dict = {}
    for item in response:
        line = item.get('line')
        del item['line']
        normalized_dict[line] = item
    return normalized_dict


def handle(event, context):
    print "Fetching status from IMTF API..."

    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('imtf-test')

    response = table.meta.client.batch_get_item(
        RequestItems={
            'imtf-test': {
                'Keys': [{'line': line, 'date': 'latest'} for line in TRAIN_LINES]
            }
        }
    )
    latest = _normalize_dynamo_response(response.get('Responses').get('imtf-test'))
    return latest


if __name__ == '__main__':
    print(handle('', ''))
