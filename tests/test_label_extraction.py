from emailtrail import extract_from_label, extract_received_by_label, remove_details, extract_protocol_used


def test_from_label_extraciton():
    cases = [
        # [input , expected_output]
        [
            "from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@pandawarrior.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Tue, 12 Jan 2016 10:20:45 -0800 (PST)",
            "mail-vk0-x233.google.com"
        ],
        [  # no from label
            "by 10.31.236.194 with SMTP id k185csp2841185vkh;\n        Tue, 12 Jan 2016 10:15:05 -0800 (PST)",
            ""
        ],
        [
            "from blah",
            "blah"
        ],
        [
            "from [127.0.0.1] (localhost [52.2.54.97])\\n\\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id p3iTfjpIQMuPA35Cjv4UrQ\\n\\tfor <support+chat@pandakungfu.com>; Wed, 16 Dec 2015 22:19:22.596 +0000 (UTC)",
            "[127.0.0.1]"
        ]
    ]

    for case in cases:
        assert case[1] == extract_from_label(case[0])


def test_detail_removal():
    cases = [
        [
            'from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n',
            'from mail-vk0-x233.google.com  \n'
        ]
    ]

    for case in cases:
        assert case[1] == remove_details(case[0])


def test_recieved_by_label_extraction():
    cases = [
        # [input , expected_output]
        [
            "by mail-vk0-x233.google.com with SMTP id k1so247736857vkb.2 \n for <support@buddy.com>; Tue, 12 Jan 2016 10:20:45 -0800 (PST)",
            "mail-vk0-x233.google.com"
        ],
        [
            "by 10.31.236.194 with SMTP id k185csp2841185vkh;\n        Tue, 12 Jan 2016 10:15:05 -0800 (PST)",
            "10.31.236.194"
        ],
        [
            "from blah",
            ""
        ],
        [
            "from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@pandawarrior.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Tue, 12 Jan 2016 10:20:45 -0800 (PST)",
            "mx.google.com"
        ],
        [
            'from [127.0.0.1] (localhost [52.2.54.97])\\n\\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id GiHVpachST-HTO7pZjZZgw\n\tfor <support+chat@buddy.com>; Tue, 12 Jan 2016 18:20:00.301 +0000 (UTC)',
            'ismtpd0002p1iad1.sendgrid.net'
        ],
        [
            """
            from [10.10.0.116] (unknown [10.10.0.116])
            (Authenticated sender: ab@lol.com)
            by mail.yolo.com (Postfix) with ESMTPSA id 96D1950E0C3A
            for <support+r.rv9cu.1647381@apple.com>; Tue, 12 Jan 2016 15:40:43 +0000 (GMT)
            """,
            'mail.yolo.com'
        ],
        [
            'from [127.0.0.1] (localhost [52.2.54.97])\\n\\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id p3iTfjpIQMuPA35Cjv4UrQ\\n\\tfor <support+chat@pandakungfu.com>; Wed, 16 Dec 2015 22:19:22.596 +0000 (UTC)',
            'ismtpd0002p1iad1.sendgrid.net'
        ]
    ]

    for case in cases:
        assert case[1] == extract_received_by_label(case[0])


def test_protocol_extraction():

    cases = [
        [
            'by mail-vk0-x233.google.com with SMTP id k1so247736857vkb.2\n        for <support@peacedojo.com>; Tue, 12 Jan 2016 10:20:45 -0800 (PST)',
            'SMTP'
        ],
        [
            'by 10.31.214.5 with HTTP; Tue, 12 Jan 2016 10:20:05 -0800 (PST)',
            'HTTP'
        ],
        [
            'from laughingbuddha.com ([5.175.233.84]:53519 helo=5.175.233.84)\n\tby ivyfpysq.laughingbuddha.com with esmtpa (Exim 4.86)\n\t(envelope-from <newsletter@indiaretailnews.com>)\n\tid 1aJ3Wi-0007QT-T2\n\tfor careers@peacedojo.com; Tue, 12 Jan 2016 19:18:40 +0100',
            'esmtpa'
        ],
        [
            'from www.ramayan.nl ([212.178.196.87])\nby smtp.ramayan.nl (Kerio Connect 8.1.2)\nfor sales@peacedojo.com;\n Fri, 18 Dec 2015 10:11:37 +0100',
            ''
        ],
        [
            'from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@peacedojo.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Tue, 12 Jan 2016 10:20:45 -0800 (PST)',
            'ESMTPS'
        ],
        [
            'from MBX7.superpower2020.com (2002:2eaf:356b::2eaf:356b) by\n MBX5.superpower2020.com (2002:2eaf:3569::2eaf:3569) with Microsoft SMTP\n Server (TLS) id 15.0.1104.5; Tue, 12 Jan 2016 17:39:59 +0000',
            'Microsoft SMTP  Server'
        ],
        [
            'from BLU179-W55 ([65.55.111.73]) by BLU004-OMC2S38.hotmail.com over TLS secured channel with Microsoft SMTPSVC(7.5.7601.23008);\n\t Tue, 12 Jan 2016 09:44:09 -0800',
            'Microsoft SMTPSVC'
        ],
        [
            'from [127.0.0.1] (localhost [52.2.54.97])\n\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id p3iTfjpIQMuPA35Cjv4UrQ\\n\\tfor <support+chat@pandakungfu.com>; Wed, 16 Dec 2015 22:19:22.596 +0000 (UTC)',
            'ESMTP'
        ]
    ]

    for case in cases:
        assert case[1] == extract_protocol_used(case[0])
