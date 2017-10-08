"""
just a quick and dirty driver program to test the analysis on a collection of email headers

my dataset:-
    1. connect to a database with sequel pro
    2. select email source.
    3. export as xml

you will need to make some adjustments to iterate over email headers as per your data

run (from project root):
$ python -m analyse_dataset.run > out.txt

This will create 3 files:
    out.txt         : analysis for each email
    delay_error.txt : pair of recieved-headers for which delay couldn't be calculated
    label_error.txt : recieved-header for which host, protocol etc. was not extracted
                      properly. (need a better regex for this)
"""
import os
from pprint import pprint
import xmltodict
from emailtrail import analyze

if __name__ == '__main__':

    filename = 'query_result_10000.xml'
    dirname = 'dataset'

    current_dir = os.path.dirname(__file__)

    with open(os.path.join(current_dir, dirname, filename)) as fd:
        doc = xmltodict.parse(fd.read())

    total_delay_error = 0
    total_label_error = 0
    total_parse_error = 0
    for row in doc['support_novo']['custom']['row']:

        mail_header = row['source']
        analysis = analyze(mail_header)

        if analysis is not None:
            total_delay_error += analysis['delay_error_count']
            total_label_error += analysis['label_error_count']

            # Print the headers with label errors
            with open("label_error.txt", "a") as myfile:
                for hop in analysis['trail']:
                    if hop['label_error']:
                        myfile.write(hop['label_error'])
                        myfile.write('\n\n\n---------------------------------------------\n\n\n')

            # Print the pair of headers we could not calculate the delay for
            with open("delay_error.txt", "a") as myfile:
                for hop in analysis['trail']:
                    if hop['delay_error']:
                        header_pair = hop['delay_error']
                        myfile.write(header_pair['current'])
                        myfile.write('\n')
                        myfile.write(header_pair['previous'])
                        myfile.write('\n\n\n---------------------------------------------\n\n\n')

            pprint(analysis)
            print '\n\n----------------------------------------\n\n'
        else:
            total_parse_error += 1

    pprint(total_parse_error)
    pprint(total_delay_error)
    pprint(total_label_error)
