from emailtrail import analyse, analyse_hop, set_delay_information


def test_hop_analysis():
    cases = [
        [
            'from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@peacedojo.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Wed, 16 Dec 2015 16:34:34 -0600',
            {
                "from": "mail-vk0-x233.google.com",
                "receivedBy": "mx.google.com",
                "protocol": "ESMTPS",
                "timestamp": 1450305274
            }
        ],
        [
            'by mailr.blah.com for <sales@hohoho.com>; Fri, 18 Dec 2015 15:37:27 GMT',
            {
                'from': '',
                'receivedBy': 'mailr.blah.com',
                'protocol': '',
                'timestamp': 1450453047
            }
        ]
    ]

    for case in cases:
        assert case[1] == analyse_hop(case[0])


def test_adding_delay_information():
    hop_list = [
        {
            'from': '',
            'protocol': 'HTTP',
            'receivedBy': '10.31.102.130',
            'timestamp': 1452574216
        },
        {
            'from': '',
            'protocol': 'SMTP',
            'receivedBy': 'mail-vk0-x22b.google.com',
            'timestamp': 1452574218
        },
        {
            'from': 'mail-vk0-x22b.google.com',
            'protocol': 'ESMTPS',
            'receivedBy': 'mx.google.com',
            'timestamp': 1452574218
        }
    ]

    expected = [
        {
            'from': '',
            'protocol': 'HTTP',
            'receivedBy': '10.31.102.130',
            'timestamp': 1452574216,
            'delay': 0
        },
        {
            'from': '',
            'protocol': 'SMTP',
            'receivedBy': 'mail-vk0-x22b.google.com',
            'timestamp': 1452574218,
            'delay': 2
        },
        {
            'from': 'mail-vk0-x22b.google.com',
            'protocol': 'ESMTPS',
            'receivedBy': 'mx.google.com',
            'timestamp': 1452574218,
            'delay': 0
        }
    ]

    assert expected == set_delay_information(hop_list)


def test_analysis():
    headers = """
    Delivered-To: money@capitalism.com
Received: by 10.129.52.209 with SMTP id b200csp1430876ywa;
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
X-Received: by 10.31.153.20 with SMTP id b20mr6116862vke.110.1507623422746;
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
Received: from mail-sor-f65.google.com (mail-sor-f65.google.com. [209.85.220.65])
        by mx.google.com with SMTPS id b31sor1345013uaa.124.2017.10.10.01.17.02
        for <money@capitalism.com>
        (Google Transport Security);
        Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
Received-SPF: pass (google.com: domain of bags@test_email.ua.edu designates 209.85.220.65 as permitted sender) client-ip=209.85.220.65;
X-Received: by 10.176.85.196 with SMTP id w4mr6874179uaa.75.1507623422198; Tue, 10 Oct 2017 01:17:02 -0700 (PDT)
MIME-Version: 1.0
Received: by 10.103.79.86 with HTTP; Tue, 10 Oct 2017 01:17:01 -0700 (PDT)
From: Mr. Money Bags <bags@moneyrules.com>
Date: Tue, 10 Oct 2017 01:17:01 -0700
Subject:
To: money@capitalism.com;
Content-Type: text/plain; charset="UTF-8"
Bcc: satan@wallstreet.com

A business opportunity awaits
"""
    expected_analysis = {
        'Bcc': u'satan@wallstreet.com',
        'Cc': u'None',
        'From': u'Mr. Money Bags <bags@moneyrules.com>',
        'To': u'money@capitalism.com;',
        'total_delay': 1,
        'trail': [
            {
                'delay': 0,
                'from': '',
                'protocol': 'HTTP',
                'receivedBy': '10.103.79.86',
                'timestamp': 1507623421
            },
            {
                'delay': 1,
                'from': 'mail-sor-f65.google.com',
                'protocol': 'SMTPS',
                'receivedBy': 'mx.google.com',
                'timestamp': 1507623422
            },
            {
                'delay': 0,
                'from': '',
                'protocol': 'SMTP',
                'receivedBy': '10.129.52.209',
                'timestamp': 1507623422
            }
        ]
    }

    assert expected_analysis == analyse(headers)
