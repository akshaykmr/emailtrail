import pytest

from emailtrail import try_to_get_timestring, strip_timezone_name


class TestTimestringParsing():
    def test_exception_if_input_is_not_string(self):
        invalid_args = [[], {}, None]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                try_to_get_timestring(arg)

    def test_stripping_extra_timezone_name(self):
        cases = [
            # [ input, expected_output]
            ['Wed, 16 Dec 2015 11:35:21 -0800 (PST)', 'Wed, 16 Dec 2015 11:35:21 -0800'],
            ['2015-12-16 19:35:09.561998041 +0000 (UTC)', '2015-12-16 19:35:09.561998041 +0000']
        ]

        for case in cases:
            assert case[1] == strip_timezone_name(case[0])

    def test_parsing(self):
        cases = [
            # [input, expected_output]
            [
                "by 10.66.248.3 with SMTP id yi3csp3166871pac;\\n        Wed, 16 Dec 2015 11:35:21 -0800 (PST)",
                "Wed, 16 Dec 2015 11:35:21 -0800"
            ],
            [
                "from o1.email.pandawarrior.com (o1.email.pandawarrior.com. [192.254.121.229])\\n        by mx.google.com with ESMTPS id sa1si40590233igb.58.2015.12.16.12.15.05\\n        for <sales.outbound@pandawarrior.com>\\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\\n        Wed, 16 Dec 2015 12:15:06 -0800 (PST)",
                "Wed, 16 Dec 2015 12:15:06 -0800"
            ],
            [
                "by filter0552p1mdw1.sendgrid.net with SMTP id filter0552p1mdw1.16694.5671BCED35\\n        2015-12-16 19:35:09.561998041 +0000 UTC",
                "2015-12-16 19:35:09.561998041 +0000"
            ],
            [
                "by filter0552p1mdw1.sendgrid.net with SMTP id filter0552p1mdw1.16694.5671BCED35\\n        2015-12-16 19:35:09.561998041 -0000 UTC",
                "2015-12-16 19:35:09.561998041 +0000"
            ],

        ]

        for case in cases:
            assert case[1] == try_to_get_timestring(case[0])
       