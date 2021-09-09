"""
just a quick and dirty driver program to test the analysis on a collection of email headers

my dataset:-
    1. connect to a database with sequel pro
    2. select email source.
    3. export as xml

you will need to make some adjustments to iterate over email headers as per your data

run (from project root):
$ python -m analyse_dataset.run > out.txt
"""
import os
from pprint import pprint
import xmltodict
from emailtrail import analyse

if __name__ == "__main__":

    filename = "query_result_10000.xml"
    dirname = "dataset"

    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, dirname, filename)) as fd:
        doc = xmltodict.parse(fd.read())

    total_parse_error = 0
    for row in doc["support_novo"]["custom"]["row"]:

        mail_header = row["source"]
        analysis = analyse(mail_header)

        if analysis is not None and analysis["trail"] is not None:
            pprint(analysis)
            print("\n\n----------------------------------------\n\n")
        else:
            total_parse_error += 1

    pprint(total_parse_error)
