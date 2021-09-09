<h2 align="center"> EmailTrail </h2> <br>
<p align="center">
<!-- <img alt="logo" title="logo" src="http://i.imgur.com/VShxJHs.png" width="450"> -->
</p>

[![Travis branch](https://img.shields.io/travis/akshayKMR/emailtrail/master.svg?style=flat-square)](https://travis-ci.org/akshayKMR/emailtrail)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)


Analyse hops taken by an Email to reach you. Get structured information about each hop - Hostnames, Protocol used, Timestamp, and Delay. [Try it out in your browser](https://emailtrail.herokuapp.com/)


**Only tested with Python 3.9**

**In your project:** `pip install emailtrail` or if you use [poetry](https://python-poetry.org/) like me `poetry add emailtrail`

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
## Table of Contents

- [Usage](#usage)
- [Caveats](#caveats)
- [Contributing](#contributing)
- [Miscellaneous](#miscellaneous)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Usage

We can analyse an email source or raw headers
```python
email = """
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
```

#### Lets analyse it

```python
import emailtrail
emailtrail.analyse_headers(email)
```

```python
Trail(
  to_address='money@capitalism.com;',
  from_address='Mr. Money Bags <bags@moneyrules.com>', cc='', bcc='satan@wallstreet.com',
  hops=[
    Hop(from_host='',
      protocol='HTTP',
      received_by_host='10.103.79.86',
      timestamp=1507623421,
      delay=0
    ),
    Hop(
      from_host='mail-sor-f65.google.com',
      protocol='SMTPS',
      received_by_host='mx.google.com',
      timestamp=1507623422,
      delay=1
    ),
    Hop(
      from_host='',
      protocol='SMTP',
      received_by_host='10.129.52.209',
      timestamp=1507623422,
      delay=0
    )
  ])
```
The `analyse_headers` function returns a python dictionary.
The trail shows the email hops sorted in chronological order. Each intermediary email server adds a `Received` header to the mail, from which the module parses the following information:

- `protocol`  : e.g HTTP, SMTP etc.
- `from_host`      : The name the sending computer gave for itself
- `received_by_host`: The receiving computers name
- `timestamp` : Unix epoch

An empty string value is set for fields which couldn't be determined.
- `delay`: The delay (in seconds) is computed by taking the difference of two consecutive hops. In above example there was
a delay of `1 sec ` from `10.103.79.86` to `mx.google.com`

#### Analysing a single `Received` header

```python
>>> header = """from mail-vk0-x233.google.com (mail-vk0-x233.google.com. [2607:f8b0:400c:c05::233])\n        by mx.google.com with ESMTPS id d124si110912930vka.142.2016.01.12.10.20.45\n        for <support@peacedojo.com>\n        (version=TLS1_2 cipher=ECDHE-RSA-AES128-GCM-SHA256 bits=128/128);\n        Wed, 16 Dec 2015 16:34:34 -0600 """

>>> from emailtrail import analyse_single_header, extract_protocol, extract_from_label, extract_received_by_label, extract_timestamp

>>> extract_protocol(header)
"ESMTPS"

>>> extract_from_label(header)
"mail-vk0-x233.google.com"

>>> extract_received_by_label(header)
"mx.google.com"

>>> extract_timestamp(header)
1450305274

>>> analyse_single_header(header)
Hop(
  from_host='mail-vk0-x233.google.com',
  protocol='ESMTPS',
  received_by_host='mx.google.com',
  timestamp=1450305274
)
```



### Caveats

- Sometimes during delay calculation the timestamp difference may be negative. 
It's not possible for a server to recieve the email before previous one,
It means that either one or both of the servers clocks are off.
We assume a delay of `0` for this hop.

## Contributing
emailtrail uses [poetry](https://python-poetry.org/) for managing virtual env and package versions.
- Fork the repo and clone it.
- In project root: `poetry install`. This installs packages required for testing and linting
- Jump into your virutal env: `poetry shell`
- Running tests: `pytest`
- If you want to understand the code, read the test cases first. It's mostly regex tuned for some email dataset. We need to run this against more datasets to cover more edge cases (emails are wild!).
- Make your changes -> Pass the tests -> Push to your branch -> Create pull request -> Profit ??


### Webapp

If you are looking for the source code of the [webapp](https://emailtrail.herokuapp.com/) in the description, you can find it [over here](https://github.com/akshayKMR/emailtrail-webapp). It's a little python webserver and a single page frontend app made with vue.js


#### Miscellaneous

In the middle of developing this module, I switched to TDD. Albeit slow for a first timer initially, It proved to be a very effective approach later on.
- Forces you to think how to structure your code.
- Less coupling, small functions with minimal to none side effects, well defined interfaces.
- Confidence in refactoring code quickly. (Everyone loves it when their investments pay off)




