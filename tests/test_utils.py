from emailtrail.utils import decode_and_convert_to_unicode, cleanup_text


def test_decode_and_convert_to_unicode():
    text = "=?utf-8?Q?Capitalism=E2=84=A2?= <money@rules.com>"
    assert "Capitalism\u2122 <money@rules.com>" == decode_and_convert_to_unicode(text)


def test_text_cleanup():
    assert "a \t b" == cleanup_text("\na \\t b \n \\n")
