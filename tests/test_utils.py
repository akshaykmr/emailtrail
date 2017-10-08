from emailtrail import strip_whitespace, cleanup_text


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
