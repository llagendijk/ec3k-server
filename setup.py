#!/usr/bin/python
import os
from distutils.core import setup
import codecs


def read(fname):
    with codecs.open(os.path.join(__file__), 'r') as fp:
        return fp.read()


setup(
    name='ec3k-server',
    version='1.1',
    description='TCP/Json Server for Energy count 3000 and compatibles',
    license='GPLv3',
    long_description=read("README.rst"),
    author='Louis Lagendijk',
    author_email='louis.lagendijk@gmail.com',
    scripts=['ec3k-server'],
    classifiers=[
        "Environment :: No Input/Output (Daemon)",
        "Development Status :: Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ])
