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
    s3 = boto3.resource('s3')

    status = {
        "date": datetime.datetime.now(TIMEZONE).strftime("%A %B %d %I:%M %p"),
        "data": data,
    }
    s3.Object('ismytrainfucked-data', str(time.time()).split('.')[0]).put(
        Body=json.dumps(status),
        ContentType="application/json"
    )

    _log_print('Wrote file to S3')
    _log_print(data)

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
