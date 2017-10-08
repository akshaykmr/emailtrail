from emailtrail import strip_whitespace, cleanup_text, decode_and_convert_to_unicode


def test_decode_and_convert_to_unicode():
    text = '=?utf-8?Q?Capitalism=E2=84=A2?= <money@rules.com>'
    assert u'Capitalism\u2122 <money@rules.com>' == decode_and_convert_to_unicode(text)


class TestWhiteSpaceStripping:
    def test_empty_list(self):
        stripped = strip_whitespace([])
        assert [] == stripped

    def test_stripping(self):
        stripped = strip_whitespace([' ', '', ' a', 'b ', ' c ', ' d e '])
        assert stripped == ['', '', 'a', 'b', 'c', 'd e']


def test_text_cleanup():
    cases = [
        'a \n',
        '\\n \n a \n   ',
        '     a     '
    ]

    for case in cases:
        assert 'a' == cleanup_text(cases[0])
