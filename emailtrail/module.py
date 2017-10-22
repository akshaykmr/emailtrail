from email.parser import HeaderParser
import re
import string
import calendar
import dateparser
import pytz

from utils import cleanup_text, decode_and_convert_to_unicode


def analyse(raw_headers):
    """
    sample output:
    {
        'To': u'robin@apple.com',
        'From': u'Dhruv <dhruv@foo.com>',
        'Cc': u'Shivam <shivam@foo.com>',
        'Bcc': u'Abhishek <quirk@foo.com>',
        'total_delay': 2,
        'trail': [
            {
                'from': '',
                'protocol': 'HTTP',
                'receivedBy': '10.31.102.130',
                'timestamp': 1452574216,
                'delay': 0
            },
            {
                'from': '',
                'protocol': 'SMTP',
                'receivedBy': 'mail-vk0-x22b.google.com',
                'timestamp': 1452574218,
                'delay': 2
            },
            {
                'from': 'mail-vk0-x22b.google.com',
                'protocol': 'ESMTPS',
                'receivedBy': 'mx.google.com',
                'timestamp': 1452574218,
                'delay': 0
            },
            {
                'from': '',
                'protocol': 'SMTP',
                'receivedBy': '10.66.77.65',
                'timestamp': 1452574218,
                'delay': 0
            }
        ]
    }
    """
    if raw_headers is None:
        return None
    raw_headers = raw_headers.strip()
    parser = HeaderParser()
    headers = parser.parsestr(raw_headers.encode('ascii', 'ignore'))
    received_headers = headers.get_all('Received')

    trail = generate_trail(received_headers)

    analysis = {
        'From': decode_and_convert_to_unicode(headers.get('From')),
        'To': decode_and_convert_to_unicode(headers.get('To')),
        'Cc': decode_and_convert_to_unicode(headers.get('Cc')),
        'Bcc': decode_and_convert_to_unicode(headers.get('Bcc')),
        'trail': trail,
        'total_delay': sum([hop['delay'] for hop in trail])
    }

    return analysis


def generate_trail(received):
    """
    Takes a list of `received` headers and
    creates the email trail (structured information of hops in transit)
    """
    if received is None:
        return None

    received = [cleanup_text(header) for header in received]
    trail = [analyse_hop(header) for header in received]

    # sort in chronological order
    trail.reverse()
    trail = set_delay_information(trail)
    return trail


def analyse_hop(header):
    """ Parses the details associated with the hop into a structured format """
    return {
        "from": extract_from_label(header),
        "receivedBy": extract_received_by_label(header),
        "protocol": extract_protocol_used(header),
        "timestamp": extract_timestamp(header)
    }


def extract_timestamp(header):
    return get_timestamp(extract_timestring(header))


def set_delay_information(hop_list):
    """ For each hop sets the calculated `delay` from previous hop | mutates list"""
    previous_timestamp = None
    for hop in hop_list:
        hop['delay'] = calculate_delay(hop['timestamp'], previous_timestamp)
        previous_timestamp = hop['timestamp']
    return hop_list


def extract_from_label(header):
    """ Get the hostname associated with `from` """
    match = re.findall(
        """
        from\s+
        (.*?)
        (?:\s+|$)
        """, header, re.DOTALL | re.X)

    return match[0] if match else ''


def extract_received_by_label(header):
    """ Get the hostname associated with `by` """
    header = re.sub('\n', ' ', header)
    header = remove_details(header)
    header = cleanup_text(header)

    if header.startswith('from'):
        match = re.findall('from\s+(?:.*?)\s+by\s+(.*?)(?:\s+|$)', header)
        return match[0] if match else ''
    elif header.startswith('by'):
        match = re.findall('by\s+(.*?)(?:\s+|$)', header)
        return match[0] if match else ''
    return ''


def extract_protocol_used(header):
    """ Get the protocol used. e.g. SMTP, HTTP etc. """
    header = re.sub('\n', ' ', header)
    header = remove_details(header)
    header = cleanup_text(header)

    protocol = ''

    if header.startswith('from'):
        match = re.findall(
            """
            from\s+(?:.*?)\s+by\s+(?:.*?)\s+
            (?:
                (?:with|via)
                (.*?)
                (?:id|$|;)
                |id|$
            )
            """, header, re.DOTALL | re.X)
        protocol = match[0] if match else ''
    if header.startswith('by'):
        match = re.findall(
            """
            by\s+(?:.*?)\s+
            (?:
                (?:with|via)
                (.*?)
                (?:id|$|;)
                |id|$
            )
            """, header, re.DOTALL | re.X)
        protocol = match[0] if match else ''

    return cleanup_text(protocol)


def extract_timestring(header):
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

    timestring = cleanup_text(remove_details(timestring))
    timestring = strip_timezone_name(timestring)
    timestring = re.sub('-0000', '+0000', timestring)

    return timestring


def remove_details(text):
    return re.sub('([(].*?[)])', ' ', text)


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

    date = dateparser.parse(timestring)
    if date is None:
        return None

    date = date.astimezone(pytz.utc)
    return calendar.timegm(date.utctimetuple())


def calculate_delay(current_timestamp, previous_timestamp):
    """ Returns delay for two unix timestamps """
    if current_timestamp is None or previous_timestamp is None:
        return 0

    delay = current_timestamp - previous_timestamp
    if delay < 0:
        # It's not possible for the current server to receive the email before previous one
        # It means that either one or both of the servers clocks are off.
        # We assume a delay of 0 in this case
        delay = 0
    return delay


def get_path_delay(current, previous, timestamp_parser=get_timestamp, timestring_parser=extract_timestring):
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
