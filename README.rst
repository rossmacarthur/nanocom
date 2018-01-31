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

  -h, --help       Show this message and exit.
  -v, --version    Show the version and exit.
  -p, --port       The serial port. Examples include /dev/tty.usbserial or /dev/ttyUSB0.
  -b, --baudrate   The baudrate of the serial port. The default is 115200.
  -c, --exit-char  The exit character (A to Z, [, \, ], or _) where Ctrl+<value> is used to exit. The default is ].


Why another serial client?
--------------------------

I couldn't find anything to suit my need. I just wanted to talk to a Raspberry Pi through the serial terminal just as I would do with SSH! I tried many different things, from GNU Screen to bash scripts. But they all were either too clunky, interfered with ``tmux``, or didn't pass ANSI escape codes through. The best thing I found was ``python -m serial.tools.miniterm`` but it had an odd menu system that wasn't needed. Nanocom is a simple modification of ``serial.tools.miniterm``.
