Software receiver server for EnergyCount 3000
=============================================

This server allows you to receive and decode radio transmissions from
EnergyCount 3000 energy loggers using a RTL-SDR supported radio receiver
and the ec3k module and send the information as json telegrams to consumers
like Domoticz over a TCP connection and/or a MQTT-server.
Data can also be retrieved from a remote ec3k-server to be consolidated in
the output from the local server.

Usage:
------
# ec3k-server --help
usage: ec3k-server [-h] [-c CONFIGFILE]

Ec3k json server.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configfile CONFIGFILE
                        configfile, default: /etc/ec3k-server.conf

The configuration file and the systemd unitfile are  installed by 
python setup.py install.

All configuration is done in the config file.


Requirements
------------
This server requuires the ec3k module which in its turn has its requirements.
See: https://github.com/avian2/ec3k as well as:
- setuptools
- configparser
- argparser

Known problems
--------------
None yet.

Feedback
--------

Please send patches or bug reports to <louis.lagendijk@gmail.com>



Source
------

You can get a local copy of the development repository with::

    git clone git://github.com/llagendijk/ec3k-server.git


License

ec3k-server, the server software:

Copyright (C) 2019 Louis Lagendijk <louis.lagendijk@gmail.com>

Protocol reverse engineering: http://forum.jeelabs.net/comment/4020

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

..
    vim: set filetype=rst:
