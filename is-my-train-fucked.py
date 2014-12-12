from lxml import etree
from tabulate import tabulate
from flask import Flask
app = Flask(__name__)

def generate_last_line(firstLine):
    status = "NOPE"
    if firstLine == "GOOD SERVICE":
        status = "YUP"
    return status

def generate_statuses():
    print "Fetching status from MTA"
    tree = etree.parse("http://web.mta.info/status/serviceStatus.txt")
    root = tree.getroot()

    status_list = [
            [item[0].text, item[1].text, generate_last_line(item[1].text)] for item in root[2]
            ]
    return status_list

@app.route('/')
def is_my_train_fucked():

    tabbed_statuses = tabulate(generate_statuses(), headers=["Subway Line", "Status", "Is it fucked?"])

    html = '''
<html>
<pre>
{}
<br />
source code <a href="https://github.com/Cbeck527/is-my-train-fucked">on github</a>
</pre>
</html>
'''.format(tabbed_statuses)
    return html

if __name__ == '__main__':
    app.run()
