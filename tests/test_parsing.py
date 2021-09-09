import pytest

from emailtrail import extract_timestring, strip_timezone_name, get_timestamp


class TestTimestringParsing:
    def test_exception_if_input_is_not_string(self):
        invalid_args = [[], {}, None]
        for arg in invalid_args:
            with pytest.raises(TypeError):
                extract_timestring(arg)

    @pytest.mark.parametrize(
        "raw, expected",
        [
            (
                "Wed, 16 Dec 2015 11:35:21 -0800 (PST)",
                "Wed, 16 Dec 2015 11:35:21 -0800",
            ),
            (
                "2015-12-16 19:35:09.561998041 +0000 (UTC)",
                "2015-12-16 19:35:09.561998041 +0000",
            ),
        ],
    )
    def test_stripping_extra_timezone_name(self, raw, expected):
        assert strip_timezone_name(raw) == expected

    @pytest.mark.parametrize(
        "raw, expected",
        [
            (
                "by 10.66.248.3 with SMTP id yi3csp3166871pac;\\n        Wed, 16 Dec 2015 11:35:21 -0800 (PST)",
                "Wed, 16 Dec 2015 11:35:21 -0800",
            ),
            (
                "from o1.email.pandawarrior.com (o1.email.pandawarrior.com. [192.254.121.229])\\n        by mx.google.com with ESMTPS id sa1si40590233igb.58.2015.12.16.12.15.05\\n        for <sales.outbound@pandawarrior.com>\\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\\n        Wed, 16 Dec 2015 12:15:06 -0800 (PST)",
                "Wed, 16 Dec 2015 12:15:06 -0800",
            ),
            (
                "by filter0552p1mdw1.sendgrid.net with SMTP id filter0552p1mdw1.16694.5671BCED35\\n        2015-12-16 19:35:09.561998041 +0000 UTC",
                "2015-12-16 19:35:09.561998041 +0000",
            ),
            (
                "by filter0552p1mdw1.sendgrid.net with SMTP id filter0552p1mdw1.16694.5671BCED35\\n        2015-12-16 19:35:09.561998041 -0000 UTC",
                "2015-12-16 19:35:09.561998041 +0000",
            ),
            (
                "by mx0032p1mdw1.sendgrid.net with SMTP id mpeXBqGIOM Sat, 16 Dec 2017 07:12:45 +0000 (UTC)",
                "Sat, 16 Dec 2017 07:12:45 +0000",
            ),
        ],
    )
    def test_parsing(self, raw, expected):
        assert extract_timestring(raw) == expected


class TestTimestampParsing:
    def test_none_input(self):
        # should return none if the input was none
        assert None is get_timestamp(None)

    def test_unsupported_timestring_returns_none(self):
        assert None is get_timestamp("time is 12:30 pm, blah")

    def test_unix_timestamp_for_valid_timestring(self):
        assert 1450305274 == get_timestamp("Wed, 16 Dec 2015 16:34:34 -0600")
        assert 1450304362 == get_timestamp("Wed, 16 Dec 2015 22:19:22.596 +0000")
        assert 1450453047 == get_timestamp("Fri, 18 Dec 2015 15:37:27 GMT")
