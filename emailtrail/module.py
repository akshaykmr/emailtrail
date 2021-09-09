from email.parser import HeaderParser
import re
import calendar
import dateparser
import pytz
from typing import List

from .utils import cleanup_text, decode_and_convert_to_unicode
from .models import Trail, Hop


def analyse_headers(raw_headers: str) -> Trail:
    """
    raw_headers: plain email source, or just headers text. e.g text value of "show original" in
    gmail.
    sample output:
    Trail(
    to_address='money@capitalism.com;',
    from_address='Mr. Money Bags <bags@moneyrules.com>', cc='', bcc='satan@wallstreet.com',
    hops=[
        Hop(from_host='',
        protocol='HTTP',
        received_by_host='10.103.79.86',
        timestamp=1507623421,
        delay=0
        ),
        Hop(
        from_host='mail-sor-f65.google.com',
        protocol='SMTPS',
        received_by_host='mx.google.com',
        timestamp=1507623422,
        delay=1
        ),
        Hop(
        from_host='',
        protocol='SMTP',
        received_by_host='10.129.52.209',
        timestamp=1507623422,
        delay=0
        )
    ])
    """
    if raw_headers is None:
        raise TypeError("empty headers")
    raw_headers = raw_headers.strip()
    parser = HeaderParser()
    headers = parser.parsestr(raw_headers)
    received_headers = headers.get_all("Received")

    trail = analyse_hops(received_headers)

    return Trail(
        from_address=decode_and_convert_to_unicode(headers.get("From")),
        to_address=decode_and_convert_to_unicode(headers.get("To")),
        cc=decode_and_convert_to_unicode(headers.get("Cc")),
        bcc=decode_and_convert_to_unicode(headers.get("Bcc")),
        hops=trail,
    )


def analyse_hops(received: str) -> List[Hop]:
    """
    Takes a list of `received` headers and
    creates the email trail (structured information of hops in transit)
    """
    if received is None:
        return []

    received = [cleanup_text(header) for header in received]
    hops = [analyse_single_header(header) for header in received]

    # sort in chronological order
    hops.reverse()
    return hops_with_delay_information(hops)


def analyse_single_header(header: str) -> Hop:
    """Parses the details associated with the hop into a structured format"""
    return Hop(
        from_host=extract_from_label(header),
        received_by_host=extract_received_by_label(header),
        protocol=extract_protocol(header),
        timestamp=extract_timestamp(header),
    )


def extract_timestamp(header: str) -> int:
    return get_timestamp(extract_timestring(header))


def hops_with_delay_information(hop_list: List[Hop]) -> List[Hop]:
    """
    For each hop sets the calculated `delay` from previous hop
    NOTE: Mutates list
    """
    previous_timestamp = None
    for hop in hop_list:
        hop.delay = calculate_delay(hop.timestamp, previous_timestamp)
        previous_timestamp = hop.timestamp
    return hop_list


def extract_from_label(header: str) -> str:
    """Get the hostname associated with `from`"""
    match = re.findall(
        r"""
        from\s+
        (.*?)
        (?:\s+|$)
        """,
        header,
        re.DOTALL | re.X,
    )

    return match[0] if match else ""


def extract_received_by_label(header: str) -> str:
    """Get the hostname associated with `by`"""
    header = re.sub(r"\n", " ", header)
    header = remove_details(header)
    header = cleanup_text(header)

    if header.startswith("from"):
        match = re.findall(r"from\s+(?:.*?)\s+by\s+(.*?)(?:\s+|$)", header)
        return match[0] if match else ""
    elif header.startswith("by"):
        match = re.findall(r"by\s+(.*?)(?:\s+|$)", header)
        return match[0] if match else ""
    return ""


def extract_protocol(header: str) -> str:
    """Get the protocol used. e.g. SMTP, HTTP etc."""
    header = re.sub(r"\n", " ", header)
    header = remove_details(header)
    header = cleanup_text(header)

    protocol = ""

    if header.startswith("from"):
        match = re.findall(
            r"""
            from\s+(?:.*?)\s+by\s+(?:.*?)\s+
            (?:
                (?:with|via)
                (.*?)
                (?:id|$|;)
                |id|$
            )
            """,
            header,
            re.DOTALL | re.X,
        )
        protocol = match[0] if match else ""
    if header.startswith("by"):
        match = re.findall(
            r"""
            by\s+(?:.*?)\s+
            (?:
                (?:with|via)
                (.*?)
                (?:id|$|;)
                |id|$
            )
            """,
            header,
            re.DOTALL | re.X,
        )
        protocol = match[0] if match else ""

    return cleanup_text(protocol)


def extract_timestring(header: str) -> str:
    """
    Tries to extract a timestring from a header
    Returns None or a String that *could* be a valid timestring
    """
    if type(header) != str:
        raise TypeError

    header = cleanup_text(header)
    timestring = None

    split_by_semicolon = header.split(";")
    split_by_newline = header.split("\n")
    split_by_id = re.split(r"\s+id\s+[^\s]*\s+", header)

    if len(split_by_semicolon) > 1:
        timestring = split_by_semicolon[-1]
    elif len(split_by_semicolon) == 1:
        if len(split_by_newline) > 1:
            # find it on the last line
            timestring = split_by_newline[-1]
        elif len(split_by_id) > 1:
            # find it after` id abc.xyz `
            timestring = split_by_id[-1]

    if timestring is None:
        return None

    timestring = cleanup_text(timestring)
    timestring = cleanup_text(remove_details(timestring))
    timestring = strip_timezone_name(timestring)
    timestring = re.sub(r"-0000", "+0000", timestring)

    return timestring


def remove_details(text: str) -> str:
    return re.sub(r"([(].*?[)])", " ", text)


def strip_timezone_name(timestring: str) -> str:
    """Removes extra timezone name at the end. eg: "-0800 (PST)" -> "-0800" """
    pattern = r"([+]|[-])([0-9]{4})[ ]([(]([a-zA-Z]{3,4})[)]|([a-zA-Z]{3,4}))"
    if re.search(pattern, timestring) is None:
        return timestring

    split = timestring.split(" ")
    split.pop()
    return " ".join(split)


def get_timestamp(timestring: str) -> int:
    """Convert a timestring to unix timestamp"""

    if timestring is None:
        return None

    date = dateparser.parse(timestring)
    if date is None:
        return None

    date = date.astimezone(pytz.utc)
    return calendar.timegm(date.utctimetuple())


def calculate_delay(current_timestamp: int, previous_timestamp: int) -> int:
    """Returns delay for two unix timestamps"""
    if current_timestamp is None or previous_timestamp is None:
        return 0

    delay = current_timestamp - previous_timestamp
    if delay < 0:
        # It's not possible for the current server to receive the email before previous one
        # It means that either one or both of the servers clocks are off.
        # We assume a delay of 0 in this case
        delay = 0
    return delay


def get_path_delay(
    current,
    previous,
    timestamp_parser=get_timestamp,
    timestring_parser=extract_timestring,
):
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
