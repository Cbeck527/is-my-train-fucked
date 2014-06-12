from lxml import etree
from tabulate import tabulate
from flask import Flask
app = Flask(__name__)


tree = etree.parse("http://web.mta.info/status/serviceStatus.txt")
root = tree.getroot()

def generate_last_line(firstLine):
    if firstLine == "GOOD SERVICE":
        status = "NOPE"
    else:
        status = "YUP"
    return status

status_list = [ [item[0].text, item[1].text, generate_last_line(item[1].text)] for item in root[2] ]

# print tabulate(status_list, headers=["Subway Line", "Status", "Is it fucked?"])

@app.route('/')
def is_my_train_fucked():

    return '<html><pre>' +  tabulate(status_list, headers=["Subway Line", "Status", "Is it fucked?"]) + '</pre></html>'

if __name__ == '__main__':
    app.run()
