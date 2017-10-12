from emailtrail import utils


def test_decode_and_convert_to_unicode():
    text = '=?utf-8?Q?Capitalism=E2=84=A2?= <money@rules.com>'
    assert u'Capitalism\u2122 <money@rules.com>' == utils.decode_and_convert_to_unicode(text)


def test_text_cleanup():
    cases = [
        'a \n',
        '\\n \n a \n   ',
        '     a     '
    ]

    for case in cases:
        assert 'a' == utils.cleanup_text(cases[0])
