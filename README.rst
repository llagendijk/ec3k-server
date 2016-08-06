Software receiver server for EnergyCount 3000
=============================================

This server allows you to receive and decode radio transmissions from
EnergyCount 3000 energy loggers using a RTL-SDR supported radio receiver
and the ec3k module and send the information as json telegrams to users
ilike Domoticz over a TCP connection.

Usage:
------
# ec3k-server --help

usage: ec3k-server [-h] [-f FREQUENCY] [-a ADDRESS] [-p PORT]

Ec3k tcp json server.

optional arguments:

        -h, --help   show this help message and exit

        -f FREQUENCY, --frequency FREQUENCY

        -a ADDRESS, --address ADDRESS

        -p PORT, --port PORT


The -f/--frequency argument is used to set the radio frequency
                (default: 868.320e6)

The -a/--address options are used to set the listen address for the server
                (default 127.0.0.1)

The -p/--port options are used to set the listen port for the server
                (default 3001)


Requirements
------------
This server requuires the ec3k module which in its turn has its requirements.
See: https://github.com/avian2/ec3k.

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

Copyright (C) 2016 Louis Lagendijk <louis.lagendijk@gmail.com>

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
