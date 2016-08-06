#!/usr/bin/python
import os
from distutils.core import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read

setup(name='ec3k-server',
	version='1.0',
	description='TCP/Json Server for Energy count 3000 and compatibles',
	license='GPLv3',
	long_description=read("README.rst"),
	author='Louis Lagendijk',
	author_email='louis.lagendijk@gmail.com',
	scripts = ['ec3k-server'],
	classifiers=[
		"Environment :: No Input/Output (Daemon)",
		"Development Status :: Production/Stable",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
	]
)
