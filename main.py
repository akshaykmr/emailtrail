"""
 Analyzes email headers to give some structured information
"""
from email.parser import HeaderParser
import re
import time
import string
import dateparser

def get_labels(header):
    """
    Gives structured info of mail servers involved and the protocol used
    given a 'Received' header

    {
        'from': '186.250.116.162',       # the name the sending computer gave for itself 
        'receivedBy': 'mx.google.com',   # the receiving computer's name
        'protocol': 'ESMTP',
        'timestamp': unix_epoch
    }
    """
    split  = header.split(';')[0]

    # TODO: These regex have room for improvement
    if split.startswith('from'):
        labels = re.findall(
            """
            from\s+
            (.*?)\s+
            by(.*?)
            (?:
                (?:with|via)
                (.*?)
                (?:id|$)
                |id|$
            )""", split, re.DOTALL | re.X)
    else:
        labels = re.findall(
            """
            ()by
            (.*?)
            (?:
                (?:with|via)
                (.*?)
                (?:id|$)
                |id
            )""", split, re.DOTALL | re.X)

    labels = map(
        lambda x: x.replace('\n', ' '),
        map(str.strip, labels[0])
    )
    return ({
        'from'      : labels[0],
        'receivedBy': labels[1],
        'protocol'  : labels[2],
        'timestamp' : get_timestamp(header)
    })

def strip_whitespace(string_list):
    """ strip whitespace from each list item """
    return map(str.strip, string_list)

def try_to_get_timestring(header):
    """ 
    Tries to extract a timestring from a header
    Returns None or a String that *could* be a valid timestring
    """
    timestring = None
    split = header.split(';')
    if len(split) != 1:
        timestring = strip_whitespace(split)[len(split) - 1]
    elif len(split) == 1:
        # try to find timestring on last line
        split = header.split('\n')
        timestring = strip_whitespace(split)[len(split) - 1]

    # remove envelopes if any
    timestring = re.sub('([(].*[)])', '', timestring)

    timestring = timestring.strip()

    # remove extra timezone name eg. "-0800 (PST)" -> "-0800"
    if re.search('([+]|[-])([0-9]{4})[ ]([(]([a-zA-Z]{3,4})[)]|([a-zA-Z]{3,4}))', timestring) is not None:
        split = timestring.split(' ')
        split.pop()
        timestring = string.join(split, ' ')

    # replace -0000 to +0000
    timestring = re.sub('-0000', '+0000', timestring)
    return timestring

def get_timestamp(header):
    """ Extract a unix timestamp from the header """
    timestring = try_to_get_timestring(header)

    if timestring is None:
        return None
    else:
        date = dateparser.parse(timestring)
        if date is None:
            return None
        else:
            timestamp = time.mktime(date.timetuple())

    return timestamp


def get_path_delay(current, previous):
    """
    Returns calculated delay (in seconds)  between two subsequent 'Received' headers
    Returns None if failure
    """
    # Try to extract the timestamp from these headers
    current_timestamp = get_timestamp(current)
    previous_timestamp = get_timestamp(previous)

    # can't do much here
    if current_timestamp is None or previous_timestamp is None:
        return None

    delay = int(current_timestamp - previous_timestamp)
    if delay < 0:
        delay = 0

    return delay

def analyze_header(raw_headers):
    """
    sample output:
    {
        'email_trail': [{'delay': 0,
                        'from': '',
                        'protocol': 'HTTP',
                        'receivedBy': '10.66.88.201',
                        'timestamp': 1450247123.0},
                        {'delay': 40,
                        'from': '',
                        'protocol': 'SMTP',
                        'receivedBy': 'mail-pa0-x231.google.com',
                        'timestamp': 1450247163.0},
                        {'delay': 0,
                        'from': 'mail-pa0-x231.google.com (mail-pa0-x231.google.com. [2607:f8b0:400e:c03::231])',
                        'protocol': 'ESMTPS',
                        'receivedBy': 'mx.google.com',
                        'timestamp': 1450247163.0},
                        {'delay': 0,
                        'from': '',
                        'protocol': 'SMTP',
                        'receivedBy': '10.66.248.3',
                        'timestamp': 1450247163.0}],
        'delay_error_count': 0,        
        'delay_errors': [ {current: header, previous: header}, ... ] # pair of headers for which delay error could not be calculated        
        'label_error_count': 0,
        'label_errors': [ 'header', ...]  # list of header for which labels could not be extracted
        'total_delay': 40
    }
    """
    if raw_headers is None:
        return None

    analysis = {}
    
    # Will contain details for each hop
    email_trail = []

    # parse the headers
    parser = HeaderParser()
    headers = parser.parsestr(raw_headers.encode('ascii', 'ignore'))
    # extract all 'Received' headers 
    received = headers.get_all('Received')

    analysis['From'] = headers.get('From')
    analysis['To'] = headers.get('To')
    analysis['Cc'] = headers.get('Cc')
    analysis['Content-Type'] = headers.get('Content-Type')

    if received is None:
        return None

    analysis['label_error_count'] = 0
    analysis['label_errors'] = []

    analysis['delay_error_count'] = 0
    analysis['delay_errors'] = []
    
    # iterate through 'Recieved' header list and aggregate the emails path
    # through all the mail servers along with delay
    for i in xrange(len(received)):
        current = received[i]
        try:
            previous = received[i+1]
        except IndexError:
            previous = None

        hop = {}

        try:
            labels = get_labels(current)
            hop['from'] = labels['from']
            hop['receivedBy'] = labels['receivedBy']
            hop['protocol'] = labels['protocol']
            hop['timestamp'] = labels['timestamp']
        except:
            analysis['label_error_count'] += 1
            analysis['label_errors'].append(current)

        hop['delay'] = 0
        if previous is not None:
            delay = get_path_delay(current, previous)
            if delay is None:
                analysis['delay_error_count'] += 1
                analysis['delay_errors'].append({
                    'current' : current,
                    'previous': previous
                })
            else:
                hop['delay'] = delay

        email_trail.append(hop)

    # sort in chronological order
    email_trail.reverse()
    analysis['label_errors'].reverse()
    analysis['delay_errors'].reverse()

    analysis['email_trail'] = email_trail
    analysis['total_delay'] = sum(map(lambda hop: hop['delay'], email_trail))
    return analysis

if __name__ == '__main__':
    """just a driver program to test the analysis for a given dataset
    
    my dataset:-
        1. connect to support database with sequel pro
        2. select source from mails LIMIT 10000;
        3. export as xml

    run:
    $ python email_trail.py > out.txt
    """
    from pprint import pprint
    import xmltodict
    with open('/Users/akshaykumar/query_result_10000.xml') as fd:
        doc = xmltodict.parse(fd.read())

    total_delay_error = 0
    total_label_error = 0
    total_parse_error = 0
    for row in doc['support_novo']['custom']['row']:

        mail_header = row['source']
        analysis = analyze_header(mail_header)

        if analysis is not None:
            total_delay_error += analysis['delay_error_count']
            total_label_error += analysis['label_error_count']

            # Print the headers with label errors
            label_errors = analysis.pop('label_errors', [])
            with open("label_error.txt", "a") as myfile:
                for header in label_errors:
                    myfile.write(header)
                    myfile.write('\n\n\n---------------------------------------------\n\n\n')

            # Print the pair of headers we could not calculate the delay for
            delay_errors = analysis.pop('delay_errors', [])
            with open("delay_error.txt", "a") as myfile:
                for header_pair in delay_errors:
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