#!/usr/bin/python2
import os
from setuptools import setup, find_packages
import codecs


def read(fname):
    with codecs.open(os.path.join(__file__), 'r') as fp:
        return fp.read()


def set_data_files():
    data_files = [
        ('/etc/systemd/system/', ['ec3k-server.service']),
    ]
    if not os.path.isfile('/etc/ec3k-server.conf'):
        data_files.append(('/etc/', ['ec3k-server.conf']))
    return data_files


setup(
    name='ec3k-server',
    version='2.0',
    packages=find_packages(),
    scripts=['ec3k-server'],
    package_data={
        '': ['*.rst'],
    },
    include_package_data=True,
    data_files=set_data_files(),
    description=
    'TCP/Json and MQTT Server for Energy count 3000 and compatibles',
    license='GPLv3',
    long_description=read("README.rst"),
    author='Louis Lagendijk',
    author_email='louis.lagendijk@gmail.com',
    install_requires=['configparser', 'ec3k', 'argparse'],
    classifiers=[
        "Environment :: No Input/Output (Daemon)",
        "Development Status :: Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ])
