"""
Query MTA API, and write data and HTML website to S3
"""
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
<head>
<meta name="viewport" content="initial-scale=1.0">
<style>body{{font-family:monospace}}th{{text-align: left}}a:visited{{color:#0000FF;}}</style>
</head>
<body>
{0}
<br />
last updated: {1}
<br />
source code <a href="https://github.com/Cbeck527/is-my-train-fucked">on github</a>
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

STATUS_PAGE_HTML = '''
<html>
<head>
<meta name="viewport" content="initial-scale=1.0">
<style>body{{font-family:monospace}}</style>
</head>
<body>
{0}
<br />
<br />
{1}
{2}
</body>
</html>
'''


def _log_print(message):
    print(json.dumps({'message': message}))


def _put_item_with_latest_and_timestamp(dynamo_resource, item):
    """
    Put an item into DynamoDB with the sort key set as `latest` and the actual
    timestamp.

    This function is DISABLED rn because idk how I want to store this data yet.
    """
    for timestamp in ('latest', datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d-%H-%M")):
        item['date'] = timestamp
        dynamo_resource.put_item(Item=item)


def handle(_, __):
    dynamodb = boto3.resource('dynamodb')
    imtf = dynamodb.Table('imtf-test')
    s3 = boto3.resource('s3')

    # this is gross, but I don't know a better way to get the nice dotted lines
    # in the headers right now
    data = [[
        '-------------&nbsp;',
        '------------&nbsp;',
        '---------------&nbsp;',
    ]]
    r = requests.get('http://web.mta.info/status/serviceStatus.txt')
    _log_print("Fetched status from MTA")
    soup = Soup(r.text, "html.parser")
    subway = soup.find("subway")
    for status in subway.findAll("line"):
        line = status.contents[1].contents[0]
        status_title = status.contents[3].contents[0]
        try:
            status_description = status.contents[5].contents[0].strip()
        except IndexError:
            _log_print(f"{line} doesn't have a status, assuming GOOD SERVICE")
            status_description = 'GOOD SERVICE'
        is_it_fucked = "YUP" if status_title != "GOOD SERVICE" else "NOPE"

        # TODO: figure out how I want to store data, and do this the right
        # way...
        # _put_item_with_latest_and_timestamp(imtf, {
        #         "line": line,
        #         "status_title": status_title,
        #         # "status_description": status_description,
        #         "is_it_fucked": is_it_fucked,
        # })

        s3.Object('www.ismytrainfucked.com', f"{line}.html").put(
            Body=STATUS_PAGE_HTML.format(line, status_description, GA),
            ContentType="text/html"
        )
        _log_print(f"Wrote {line}.html file to website bucket")

        data.append([
                f"<a href={line}.html>{line}</a>",
                status_title,
                is_it_fucked
        ])

    html_table = tabulate(data, headers=["Subway Line", "Status", "Is it fucked?"], tablefmt="html")
    last_updated = datetime.datetime.now(TIMEZONE).strftime("%A %B %d %I:%M %p")
    s3.Object('www.ismytrainfucked.com', 'index.html').put(
        Body=HTML.format(html_table, last_updated, GA),
        ContentType="text/html"
    )
    _log_print("Wrote index file to website bucket")
    return {'message': "ALL GOOD, YO!"}


if __name__ == '__main__':
    handle('', '')
