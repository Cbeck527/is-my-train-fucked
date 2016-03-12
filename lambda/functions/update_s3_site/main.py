from __future__ import print_function
from tabulate import tabulate

import boto3

HTML = '''
<html>
<body>
<pre>
{0}
<br />
source code <a href="https://github.com/Cbeck527/is-my-train-fucked">on github</a>
</pre>
{1}
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

print('Loading function')


def handle(event, context):
    print("EVENT:")
    print(event)
    print("***")
    data = event['Records'][0]['dynamodb']['NewImage']['data']['L']

    status = [[item['L'][0]['S'], item['L'][1]['S'], item['L'][2]['S']] for item in data]
    table = tabulate(status, headers=["Subway Line", "Status", "Is it fucked?"])

    print("Connecting to s3")
    s3 = boto3.resource('s3')
    s3.Object('www.ismytrainfucked.com', 'index.html').put(
        Body=HTML.format(table, GA), ContentType="text/html"
    )
    return 'Successfully processed {} records.'.format(len(event['Records']))
