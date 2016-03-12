import boto3
import datetime
import decimal
import requests
import time

from bs4 import BeautifulSoup as Soup

def handle(event, context):
    print "Fetching status from MTA..."
    data = []
    r = requests.get('http://web.mta.info/status/serviceStatus.txt')
    soup = Soup(r.text, "html.parser")
    for subway in soup.findAll("subway"):
        for status in subway.findAll("line"):
            line = (status.contents[1].contents[0])
            status = (status.contents[3].contents[0])
            if status != "GOOD SERVICE":
                is_it_fucked = "YUP"
            else:
                is_it_fucked = "NOPE"
            data.append([line, status, is_it_fucked])

    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('ismytrainfucked')
    status = {
        "date": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
        "time": decimal.Decimal(time.time()),
        "data": data,
    }

    table.put_item(Item=status)

    response = {"status": "OK!", "data": data}
    return response
