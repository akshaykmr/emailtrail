from email.header import decode_header, make_header


def cleanup_text(text: str) -> str:
    """
    normalizes newline/tab chars, strips whitespace, removes newline chars from the ends.
    NOTE: Only to be used for a header value.
    background context for this part is lost, need an email dataset to reiterate.
    """
    text = normalize_newlinechar(text)
    text = normalize_tabchar(text)
    return text.strip()


def normalize_newlinechar(text: str) -> str:
    return text.replace("\\n", "\n")


def normalize_tabchar(text: str) -> str:
    return text.replace("\\t", "\t")


def decode_and_convert_to_unicode(text) -> str:
    if not text:
        return ""
    try:
        header = make_header(decode_header(text))
        return str(header)
    except Exception:
        # Illegal encoding sequence used in the email header, return as is
        return text
