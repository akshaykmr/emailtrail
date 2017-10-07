from emailtrail import strip_whitespace


class TestWhiteSpaceStripping:
    def test_empty_list(self):
        stripped = strip_whitespace([])
        assert [] == stripped
    
    def test_stripping(self):
        stripped = strip_whitespace([' ', '', ' a', 'b ', ' c ', ' d e '])
        assert stripped == ['', '', 'a', 'b', 'c', 'd e']


