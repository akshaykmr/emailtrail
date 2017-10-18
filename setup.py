import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst', 'md')
except ImportError, RuntimeError:
    # Just reads README.md without the conversion
    # Why? to not force others to install pypandoc when they wanna just build the module,
    # and not upload to PyPi.
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

about = {}
with open(os.path.join(here, 'emailtrail', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['emailtrail'],
    install_requires=['dateparser'],
    license='MIT',
    long_description=read_md('README.md'),
)
