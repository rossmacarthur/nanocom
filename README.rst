nanocom
=======

An ultra simple serial client using pyserial.


Usage
-----

Install it using

::

    pip install nanocom

Example usage would be

::

    nanocom --port /dev/ttyUSB0 --baudrate 115200

The following options are available

::

  -h, --help              Show this message and exit.
  -v, --version           Show the version and exit.
  -p, --port PATH         The serial port. Examples include /dev/tty.usbserial or /dev/ttyUSB0.
  -b, --baudrate INTEGER  The baudrate of the serial port. The default is 115200.
  -m, --map KEY VALUE     A character map where a string VALUE is sent for a character KEY. Multiple maps are allowed.
  -c, --exit-char CHAR    The exit character (A to Z, [, \, ], or _) where Ctrl+CHAR is used to exit. The default is ].


Why another serial client?
--------------------------

I couldn't find anything to suit my need. I tried many different things, from GNU Screen to bash scripts. But they all were either too clunky, interfered with ``tmux``, or didn't pass ANSI escape codes through. The best thing I found was ``python -m serial.tools.miniterm`` but it had an odd menu system that wasn't needed. Nanocom is a simple modification of ``serial.tools.miniterm``.
