"""
Query MTA API, write values to DynamoDB, and write HTML website to S3
"""
from __future__ import print_function

from bs4 import BeautifulSoup as Soup
from tabulate import tabulate

import boto3
import datetime
import decimal
import json
import requests
import time


HTML = '''
<html>
<head><meta name="viewport" content="initial-scale=1.0"></head>
<body>
<pre>
{0}
<br />
source code <a href="https://github.com/Cbeck527/is-my-train-fucked">on github</a>
<br />
last updated: {1}
</pre>
{2}
</body>
</html>
'''

GA = '''
<script>
!function(f,u,c,k,e,d){f.GoogleAnalyticsObject=c;f[c]||(f[c]=function(){
(f[c].q=f[c].q||[]).push(arguments)});f[c].l=+new Date;e=u.createElement(k);
d=u.getElementsByTagName(k)[0];e.src='//www.google-analytics.com/analytics.js';
d.parentNode.insertBefore(e,d)}(window,document,'ga','script');

ga('create', 'UA-51698710-3', 'auto');
ga('send', 'pageview');
</script>
'''


def _log_print(message):
    log_entry = {
        'message': message
    }
    print(json.dumps(log_entry))


def handle(_, __):
    _log_print("Fetching status from MTA")
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

    # TODO: change the schema of this data, but talk to @MichaelACraig first
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table('ismytrainfucked')
    status = {
        "date": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
        "time": decimal.Decimal(time.time()),
        "data": data,
    }

    table.put_item(Item=status)
    _log_print('Logged to DB')
    _log_print(data)

    html_table = tabulate(data, headers=["Subway Line", "Status", "Is it fucked?"])
    last_updated = datetime.datetime.isoformat(datetime.datetime.now())
    _log_print("Connecting to s3")
    s3 = boto3.resource('s3')
    s3.Object('www.ismytrainfucked.com', 'index.html').put(
        Body=HTML.format(html_table, last_updated, GA),
        ContentType="text/html"
    )
    return {'message': "ALL GOOD, YO!"}


if __name__ == '__main__':
    handle('', '')
