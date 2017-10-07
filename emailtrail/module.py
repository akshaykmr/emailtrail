from email.parser import HeaderParser
import re
import time
import string
import dateparser


def extract_labels(header):
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
    split = header.split(';')[0]

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
        'from': labels[0],
        'receivedBy': labels[1],
        'protocol': labels[2],
        'timestamp': get_timestamp(header)
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
    pattern = '([+]|[-])([0-9]{4})[ ]([(]([a-zA-Z]{3,4})[)]|([a-zA-Z]{3,4}))'
    if re.search(pattern, timestring) is not None:
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
        'From': 'Jason Pruim <jpruim@contrax.com>',
        'To': 'support+chat@kayako.com',
        'Cc': None,
        'delay_error_count': 0,
        'trail': [{'delay': 0,
                        'from': '[127.0.0.1] (localhost [52.2.54.97])',
                        'protocol': '',
                        'receivedBy': 'ismtpd0001p1iad1.sendgr',
                        'timestamp': 1450278117.0},
                        {'delay': 0,
                        'from': '',
                        'protocol': '',
                        'receivedBy': 'filter0624p1mdw1.sendgr',
                        'timestamp': 1450278117.0},
                        {'delay': 0,
                        'from': 'o1.email.kayako.com (o1.email.kayako.com. [192.254.121.229])',
                        'protocol': 'ESMTPS',
                        'receivedBy': 'mx.google.com',
                        'timestamp': 1450249321.0},
                        {'delay': 0,
                        'from': '',
                        'protocol': 'SMTP',
                        'receivedBy': '10.66.248.3',
                        'timestamp': 1450249321.0}],
        'label_error_count': 0,
        'total_delay': 0
    }
    """
    if raw_headers is None:
        return None

    analysis = {}

    # Will contain details for each hop
    trail = []

    # parse the headers
    parser = HeaderParser()
    headers = parser.parsestr(raw_headers.encode('ascii', 'ignore'))
    # extract all 'Received' headers
    received = headers.get_all('Received')

    analysis['From'] = headers.get('From')
    analysis['To'] = headers.get('To')
    analysis['Cc'] = headers.get('Cc')

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
            previous = received[i + 1]
        except IndexError:
            previous = None

        hop = {}

        try:
            labels = extract_labels(current)
            hop['from'] = labels['from']
            hop['receivedBy'] = labels['receivedBy']
            hop['protocol'] = labels['protocol']
            hop['timestamp'] = labels['timestamp']
        except:  # TODO: get rid of this diaper
            analysis['label_error_count'] += 1
            analysis['label_errors'].append(current)

        hop['delay'] = 0
        if previous is not None:
            delay = get_path_delay(current, previous)
            if delay is None:
                analysis['delay_error_count'] += 1
                analysis['delay_errors'].append({
                    'current': current,
                    'previous': previous
                })
            else:
                hop['delay'] = delay

        trail.append(hop)

    # sort in chronological order
    trail.reverse()
    analysis['label_errors'].reverse()
    analysis['delay_errors'].reverse()

    analysis['trail'] = trail
    analysis['total_delay'] = sum(map(lambda hop: hop['delay'], trail))
    return analysis