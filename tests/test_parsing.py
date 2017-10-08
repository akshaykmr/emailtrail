import pytest

from emailtrail import try_to_get_timestring, strip_timezone_name, get_timestamp, extract_labels


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


class TestTimestampParsing():
    def test_none_input(self):
        # should return none if the input was none
        assert None is get_timestamp(None)

    def test_unsupported_timestring_returns_none(self):
        assert None is get_timestamp('time is 12:30 pm, blah')

    def test_unix_timestamp_for_valid_timestring(self):
        assert 1450263874 == get_timestamp('Wed, 16 Dec 2015 16:34:34 -0600')


def test_label_extraction():
    cases = [
        # [ input, expected_output ]
        [
            'by 10.66.248.3 with SMTP id yi3csp3166871pac;\\n        Wed, 16 Dec 2015 11:35:21 -0800 (PST)',
            {
                'from': '',
                'receivedBy': '10.66.248.3',
                'protocol': 'SMTP',
                'timestamp': 1450245921
            }
        ],
        [
            'from [10.160.25.50] ([186.250.116.162])\\n        by mx.google.com with ESMTP id h71si7136985vkd.116.2015.12.16.11.35.20\\n        for <piracy@tpb.com>;\\n        Wed, 16 Dec 2015 11:35:21 -0800 (PST)',
            {
                'from': '[10.160.25.50] ([186.250.116.162])',
                'receivedBy': 'mx.google.com',
                'protocol': 'ESMTP',
                'timestamp': 1450245921
            }
        ],
        [
            'from mx0a-000e4101.baba.com (mx0a-000e4101.baba.com. [67.231.144.73])\\n        by mx.google.com with ESMTPS id a31si3046108ioj.121.2015.12.16.14.34.35\\n        for <rajiv@pandakungfu.com>\\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\\n        Wed, 16 Dec 2015 14:34:35 -0800 (PST)',
            {
                'from': 'mx0a-000e4101.baba.com (mx0a-000e4101.baba.com. [67.231.144.73])',
                'receivedBy': 'mx.google.com',
                'protocol': 'ESMTPS',
                'timestamp': 1450256675
            }
        ]
    ]
    improvement_cases = [ # noqa
        # would be good to pass these cases. expected output can be modified if required
        [
            'from [127.0.0.1] (localhost [52.2.54.97])\\n\\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id p3iTfjpIQMuPA35Cjv4UrQ\\n\\tfor <support+chat@pandakungfu.com>; Wed, 16 Dec 2015 22:19:22.596 +0000 (UTC)',
            {
                'from': '[127.0.0.1] (localhost [52.2.54.97])',
                'receivedBy': 'ismtpd0002p1iad1.sendgrid.net',
                'protocol': 'ESMTP',
                'timestamp': 1337
            }
        ],
        [
            'by mailr.blah.com for <sales@hohoho.com>; Fri, 18 Dec 2015 15:37:27 GMT',
            {
                'from': '',
                'receivedBy': 'mailr.blah.com',
                'protocol': '',
                'timestamp': 1337
            }
        ]
    ]

    # future improvements
    # cases = cases + improvement_cases

    for case in cases:
        assert case[1] == extract_labels(case[0])
