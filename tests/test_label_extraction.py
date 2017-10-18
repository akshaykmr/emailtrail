from emailtrail import extract_from_label, extract_recieved_by_label, remove_details

def test_from_label_extraciton():
    cases = [
        # [input , expected_output]
        [
            "from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@pandawarrior.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Tue, 12 Jan 2016 10:20:45 -0800 (PST)",
            "mail-vk0-x233.google.com"
        ],
        [ # no from label
            "by 10.31.236.194 with SMTP id k185csp2841185vkh;\n        Tue, 12 Jan 2016 10:15:05 -0800 (PST)",
            ""
        ],
        [
            "from blah",
            "blah"
        ]
    ]

    for case in cases:
        assert case[1] == extract_from_label(case[0])



def test_detail_removal():
    cases = [
        [
            'from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n',
            'from mail-vk0-x233.google.com \n'
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
            'from [127.0.0.1] (localhost [52.2.54.97])\n\tby ismtpd0002p1iad1.sendgrid.net (SG) with ESMTP id GiHVpachST-HTO7pZjZZgw\n\tfor <support+chat@buddy.com>; Tue, 12 Jan 2016 18:20:00.301 +0000 (UTC)',
            'ismtpd0002p1iad1.sendgrid.net'
        ],
        [
            """
            from [10.10.0.116] (unknown [10.10.0.116])
            (Authenticated sender: ab@everymatrix.com)
            by mail.yolo.com (Postfix) with ESMTPSA id 96D1950E0C3A
            for <support+r.rv9cu.1647381@apple.com>; Tue, 12 Jan 2016 15:40:43 +0000 (GMT)
            """,
            'mail.yolo.com'
        ]
    ]

    for case in cases:
        assert case[1] == extract_recieved_by_label(case[0])
