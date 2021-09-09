import sys
from email.header import decode_header, make_header


def python_version_greater_than_three():
    return sys.version_info > (3, 0)


def cleanup_text(text):
    """
    normalizes newline/tab chars, strips whitespace, removes newline chars from the ends.
    """
    text = normalize_newlinechar(text)
    text = normalize_tabchar(text)
    return text.strip()


def normalize_newlinechar(text):
    return text.replace("\\n", "\n")


def normalize_tabchar(text):
    return text.replace("\\t", "\t")


def decode_and_convert_to_unicode(text):
    if not text:
        return ""
    try:
        header = make_header(decode_header(text))
        if python_version_greater_than_three():
            return str(header)
        else:
            return unicode(header)
    except Exception:
        # Illegal encoding sequence used in the email header, return as is
        return text
