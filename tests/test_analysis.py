import pytest
from emailtrail import (
    analyse_headers,
    analyse_single_header,
    hops_with_delay_information,
    Trail,
    Hop,
)


@pytest.mark.parametrize(
    "header,expected",
    [
        (
            "from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@peacedojo.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Wed, 16 Dec 2015 16:34:34 -0600",
            Hop(
                from_host="mail-vk0-x233.google.com",
                received_by_host="mx.google.com",
                protocol="ESMTPS",
                timestamp=1450305274,
            ),
        ),
        (
            "by mailr.blah.com for <sales@hohoho.com>; Fri, 18 Dec 2015 15:37:27 GMT",
            Hop(
                from_host="",
                received_by_host="mailr.blah.com",
                protocol="",
                timestamp=1450453047,
            ),
        ),
    ],
)
def test_hop_analysis(header, expected):
    assert analyse_single_header(header) == expected


def test_adding_delay_information():
    hop_list = [
        Hop(
            from_host="",
            protocol="HTTP",
            received_by_host="10.31.102.130",
            timestamp=1452574216,
        ),
        Hop(
            from_host="",
            protocol="SMTP",
            received_by_host="mail-vk0-x22b.google.com",
            timestamp=1452574218,
        ),
        Hop(
            from_host="mail-vk0-x22b.google.com",
            protocol="ESMTPS",
            received_by_host="mx.google.com",
            timestamp=1452574218,
        ),
    ]

    expected = [
        Hop(
            from_host="",
            protocol="HTTP",
            received_by_host="10.31.102.130",
            timestamp=1452574216,
            delay=0,
        ),
        Hop(
            from_host="",
            protocol="SMTP",
            received_by_host="mail-vk0-x22b.google.com",
            timestamp=1452574218,
            delay=2,
        ),
        Hop(
            from_host="mail-vk0-x22b.google.com",
            protocol="ESMTPS",
            received_by_host="mx.google.com",
            timestamp=1452574218,
            delay=0,
        ),
    ]

    assert hops_with_delay_information(hop_list) == expected


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
    expected_analysis = Trail(
        bcc="satan@wallstreet.com",
        cc="",
        from_address="Mr. Money Bags <bags@moneyrules.com>",
        to_address="money@capitalism.com;",
        hops=[
            Hop(
                delay=0,
                from_host="",
                protocol="HTTP",
                received_by_host="10.103.79.86",
                timestamp=1507623421,
            ),
            Hop(
                delay=1,
                from_host="mail-sor-f65.google.com",
                protocol="SMTPS",
                received_by_host="mx.google.com",
                timestamp=1507623422,
            ),
            Hop(
                delay=0,
                from_host="",
                protocol="SMTP",
                received_by_host="10.129.52.209",
                timestamp=1507623422,
            ),
        ],
    )
    assert analyse_headers(headers) == expected_analysis


def test_useless_input():
    expected_analysis = Trail(bcc="", cc="", from_address="", to_address="", hops=[])
    assert analyse_headers("") == expected_analysis


def test_none_input_returns_none():
    with pytest.raises(TypeError):
        analyse_headers(None)
