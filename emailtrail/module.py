import sys
from email.header import decode_header, make_header
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
    split = cleanup_text(header.split(';')[0])

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
        map(cleanup_text, labels[0])
    )
    return ({
        'from': labels[0],
        'receivedBy': labels[1],
        'protocol': labels[2],
        'timestamp': get_timestamp(try_to_get_timestring(header))
    })


def try_to_get_timestring(header):  # TODO: rename this func
    """
    Tries to extract a timestring from a header
    Returns None or a String that *could* be a valid timestring
    """
    if type(header) != str:
        raise TypeError

    header = cleanup_text(header)
    timestring = None

    split = header.split(';')
    if len(split) != 1:
        timestring = cleanup_text(split[len(split) - 1])
    elif len(split) == 1:
        # try to find timestring on last line
        split = header.split('\n')
        timestring = cleanup_text(split[len(split) - 1])

    # remove envelopes if any
    timestring = cleanup_text(re.sub('([(].*[)])', '', timestring))
    timestring = strip_timezone_name(timestring)
    # replace -0000 to +0000
    timestring = re.sub('-0000', '+0000', timestring)

    return timestring


def cleanup_text(text):
    """
    normalizes newline chars, strips whitespace, removes newline chars from the ends.
    """
    return normalize_newlinechar(text).strip().strip('\n').strip()


def normalize_newlinechar(text):
    return text.replace("\\n", "\n")


def strip_timezone_name(timestring):
    """ Removes extra timezone name at the end. eg: "-0800 (PST)" -> "-0800" """
    pattern = '([+]|[-])([0-9]{4})[ ]([(]([a-zA-Z]{3,4})[)]|([a-zA-Z]{3,4}))'
    if re.search(pattern, timestring) is None:
        return timestring

    split = timestring.split(' ')
    split.pop()
    return string.join(split, ' ')


def get_timestamp(timestring):
    """ Convert a timestring to unix timestamp """

    if timestring is None:
        return None
    else:
        date = dateparser.parse(timestring)
        if date is None:
            return None
        else:
            timestamp = time.mktime(date.timetuple())

    return int(timestamp)


def calculate_delay(current_timestamp, previous_timestamp):
    """ Returns delay for two unixtimestamps """
    delay = current_timestamp - previous_timestamp
    if delay < 0:
        # It's not possible for the current server to recieve the email before previous one
        # It means that either one or both of the servers clocks are off.
        # We assume a delay of 0 in this case
        delay = 0
    return delay


def decode_and_convert_to_unicode(text):
    try:
        header = make_header(decode_header(text))
        if (sys.version_info > (3, 0)):
            return str(header)
        else:
            return unicode(header)
    except Exception:
        # Illegal encoding sequence used in the email header, return as is
        return text


def get_path_delay(current, previous, timestamp_parser=get_timestamp, timestring_parser=try_to_get_timestring):
    """
    Returns calculated delay (in seconds)  between two subsequent 'Received' headers
    Returns None if not determinable
    """

    current_timestamp = timestamp_parser(timestring_parser(current))
    previous_timestamp = timestamp_parser(timestring_parser(previous))

    if current_timestamp is None or previous_timestamp is None:
        # parsing must have been unsuccessful, can't do much here
        return None

    return calculate_delay(current_timestamp, previous_timestamp)


def generate_trail(received):
    """
    Takes a list of `recieved` headers and
    creates the email trail (structured information of hops in transit)
    """
    if received is None:
        return None

    trail = []

    for i in xrange(len(received)):
        current = received[i]
        try:
            previous = received[i + 1]
        except IndexError:
            previous = None

        hop = {
            'delay': 0,
            'label_error': None,
            'delay_error': None
        }

        try:
            hop.update(extract_labels(current))
        except IndexError:  # FIXME
            hop['label_error'] = current

        if previous is not None:
            delay = get_path_delay(current, previous)
            if delay is None:
                hop['delay_error'] = {
                    'current': current,
                    'previous': previous
                }
            else:
                hop['delay'] = delay

        trail.append(hop)

    # sort in chronological order for readability
    trail.reverse()
    return trail


def generate_stats(trail):
    """ sums delay and errors """
    if trail is None:
        return None

    stats = {
        'total_delay': 0,
        'delay_error_count': 0,
        'label_error_count': 0
    }

    for hop in trail:
        stats['total_delay'] += hop['delay']

        if hop['delay_error']:
            stats['delay_error_count'] += 1
        if hop['label_error']:
            stats['label_error_count'] += 1

    return stats


def analyze(raw_headers):
    """
    sample output:

    {
        'From': 'Josh <foo.josh@gmail.com>',
        'To': 'gossip+chat@kungfu.com',
        'Cc': None,
        'delay_error_count': 0,
        'label_error_count': 0,
        'total_delay': 0,
        'trail': [
            {
                'delay': 0,
                'delay_error': None,
                'from': '[127.0.0.1] (localhost [52.2.54.97])',
                'label_error': None,
                'protocol': '',
                'receivedBy': 'ismtpd0002p1iad1.sendgr',
                'timestamp': 1451525244
            },
            {
                'delay': 0,
                'delay_error': None,
                'from': '',
                'label_error': None,
                'protocol': '',
                'receivedBy': 'filter0441p1mdw1.sendgr',
                'timestamp': 1451525244
            },
            {
                'delay': 0,
                'delay_error': None,
                'from': 'o1.email.kungfu.com (o1.email.kungfu.com. [192.254.121.229])',
                'label_error': None,
                'protocol': 'ESMTPS',
                'receivedBy': 'mx.google.com',
                'timestamp': 1451496447
            },
            {
                'delay': 0,
                'delay_error': None,
                'from': '',
                'label_error': None,
                'protocol': 'SMTP',
                'receivedBy': '10.66.248.3',
                'timestamp': 1451496447
            }
        ]
    }
    """
    if raw_headers is None:
        return None

    # parse the headers
    parser = HeaderParser()
    headers = parser.parsestr(raw_headers.encode('ascii', 'ignore'))

    # extract all 'Received' headers
    received = headers.get_all('Received')

    trail = generate_trail(received)
    stats = generate_stats(trail)

    analysis = {
        'From': decode_and_convert_to_unicode(headers.get('From')),
        'To': decode_and_convert_to_unicode(headers.get('To')),
        'Cc': decode_and_convert_to_unicode(headers.get('Cc')),
        'trail': trail,
        'stats': stats
    }

    return analysis
