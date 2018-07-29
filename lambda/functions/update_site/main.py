"""
Query MTA API, and write data and HTML website to S3
"""
from __future__ import print_function

from bs4 import BeautifulSoup as Soup
from pytz import timezone
from tabulate import tabulate

import boto3
import datetime
import json
import requests
import time


# NYC is only in one time zone
TIMEZONE = timezone('US/Eastern')

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
    print(json.dumps({'message': message}))


def _put_item_with_latest_and_timestamp(dynamo_resource, item):
    """
    Put an item into DynamoDB with the sort key set as `latest` and the actual
    timestamp.
    """
    for timestamp in ('latest', datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d-%H-%M")):
        item['date'] = timestamp
        dynamo_resource.put_item(Item=item)


def handle(_, __):
    dynamodb = boto3.resource('dynamodb')
    imtf = dynamodb.Table('imtf-test')

    _log_print("Fetching status from MTA")

    data = []
    r = requests.get('http://web.mta.info/status/serviceStatus.txt')
    soup = Soup(r.text, "html.parser")
    subway = soup.find("subway")
    for status in subway.findAll("line"):
        line = status.contents[1].contents[0]
        status_title = status.contents[3].contents[0]
        # status_description = status.contents[5].contents[0].strip()
        is_it_fucked = "YUP" if status_title != "GOOD SERVICE" else "NOPE"
        _put_item_with_latest_and_timestamp(imtf, {
                "line": line,
                "status_title": status_title,
                # "status_description": status_description,
                "is_it_fucked": is_it_fucked,
        })
        data.append([line, status_title, is_it_fucked])

    html_table = tabulate(data, headers=["Subway Line", "Status", "Is it fucked?"])
    last_updated = datetime.datetime.now(TIMEZONE).strftime("%A %B %d %I:%M %p")
    s3.Object('www.ismytrainfucked.com', 'index.html').put(
        Body=HTML.format(html_table, last_updated, GA),
        ContentType="text/html"
    )
    _log_print("Wrote index file to website bucket")
    return {'message': "ALL GOOD, YO!"}


if __name__ == '__main__':
    handle('', '')
