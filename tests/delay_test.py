from emailtrail import calculate_delay, get_path_delay


class TestDelayCalculation():
    def test_usual_cases(self):
        assert 1 == calculate_delay(1450263874, 1450263873)
        assert 0 == calculate_delay(1450263874, 1450263874)

    def test_negative_delay_returns_zero(self):
        assert 0 == calculate_delay(1450263874, 1450263876)


def test_path_delay():
    cases = [
        # [current_header,  previous_header, expected_delay]
        [   
            # has delay
            'by wr-out-0506.google.com with SMTP id 69so1099905wra for ...; Sat, 22 Mar 2007 13:02:18 -0700 (PDT)',
            'by 10.114.60.19 with SMTP id i19mr754361waa.1174593725445; Thu, 22 Mar 2007 13:02:05 -0700 (PDT)',
            13
        ],
        [   # no delay
            'by 10.66.248.3 with SMTP id yi3csp3166897pac;\\n        Wed, 16 Dec 2015 11:35:25 -0800 (PST)',
            'from o1.email.pandawarrior.com (o1.email.pandawarrior.com. [192.254.121.229])\\n        by mx.google.com with ESMTPS id h5si8278964obe.20.2015.12.16.11.35.24\\n        for <support+chat@pandawarrior.com>\\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\\n        Wed, 16 Dec 2015 11:35:25 -0800 (PST)',
            0
        ],
        [
            # not determinable case
            """
                from blah.spd.co.il (blah-2.spd.co.il. [80.178.250.57])
                by mx.google.com with ESMTP id pn4si5318530lbc.55.2015.12.16.13.24.21
                for <sales@foo.com>;
                Wed, 16 Dec 2015 13:24:21 -0800 (PST)
            """,
            'from blah.spd.co.il',
            None
        ]
    ]

    for case in cases:
        assert case[2] == get_path_delay(case[0], case[1])
