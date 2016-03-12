import boto3
import datetime
import decimal
import time

from boto3.dynamodb.conditions import Key, Attr


def handle(event, context):
    print "Fetching status from IMTF API..."

    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('ismytrainfucked')

    response = table.query(
        KeyConditionExpression=Key('date').eq(
            datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))
        & Key('time').lte(decimal.Decimal(time.time())),
        ScanIndexForward=False,
        Limit=1,
    )

    return response
