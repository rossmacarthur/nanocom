from __future__ import print_function, unicode_literals
import os
import serial
import sys
from nanocom import __version__, Nanocom, key_to_description, description_to_key


class ParserExitWithMessage(Exception):
    pass


class ParserError(Exception):
    pass


class Option(object):

    def __init__(self, identifiers, default=None, exit=None, help='', is_flag=None, type=None):
        self.name = max(identifiers, key=len).lstrip('-').replace('-', '_')
        self.identifiers = sorted(identifiers, key=len)
        self.default = default
        self.exit = exit
        self.help = help
        self.is_flag = is_flag
        self.type = type

    def __str__(self):
        return ' / '.join(self.identifiers)


class Parser(object):

    def __init__(self, help_prefix='', *options):
        self.args = sys.argv[1:]
        self.help_format = {'prog': os.path.basename(sys.argv[0])}
        self.options = list(options)
        self.options.append(Option(['-h', '--help'], is_flag=True, exit=self.help_message(help_prefix)))

    def help_message(self, help_prefix):
        helps = [('-h, --help', 'Show this message and exit.')]
        helps += [(', '.join(option.identifiers), option.help) for option in self.options]
        col = len(max((h[0] for h in helps), key=len))
        usage = 'Usage: {prog} [OPTIONS]'
        option_list = '\n'.join('  {:<{col}}  {}'.format(*h, col=col) for h in helps)
        return usage + help_prefix + '\nOptions:\n' + option_list

    def parse_id(self, option, index):
        if option.is_flag:
            if option.exit:
                raise ParserExitWithMessage(option.exit.format(**self.help_format))
            else:
                return True
        elif index + 1 >= len(self.args) or self.args[index + 1].startswith('-'):
            raise ParserError('{} requires an argument'.format(self.args[index]))

        try:
            value = self.args[index + 1]
            return option.type(value)
        except TypeError:
            raise ParserError('invalid value for {}: {} is not a valid {}'.format(
                self.args[index], value, option.type.__name__,))

    def parse(self):
        # loop through args and collect values
        for index, arg in enumerate(self.args):
            if arg.startswith('-'):
                for option in self.options:
                    if arg in option.identifiers:
                        setattr(self, option.name, self.parse_id(option, index))
                        break
                else:
                    raise ParserError('unrecognised option {}'.format(arg))

        # check all values have been set else set defaults or raise error
        for option in self.options:
            if not hasattr(self, option.name) and not option.is_flag:
                if option.default is None:
                    raise ParserError('{} is required'.format(option))
                else:
                    setattr(self, option.name, option.default)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def path(string):
    if os.path.exists(string):
        return string
    raise TypeError()


def baudrate(string):
    try:
        return int(string)
    except Exception:
        raise TypeError()


def exit_char(string):
    try:
        return description_to_key(string)
    except Exception:
        raise TypeError()


def cli():
    help_message_prefix = """
   _ __   __ _ _ __   ___   ___ ___  _ __ ___
  | '_ \\ / _` | '_ \\ / _ \\ / __/ _ \\| '_ ` _ \\
  | | | | (_| | | | | (_) | (_| (_) | | | | | |
  |_| |_|\\__,_|_| |_|\\___/ \\___\\___/|_| |_| |_|

  An ultra simple serial client using pyserial.
"""

    parser = Parser(
        help_message_prefix,

        Option(['-v', '--version'],
               is_flag=True,
               exit='{prog} ' + __version__,
               help='Show the version and exit.'),

        Option(['-p', '--port'],
               type=path,
               help='The serial port. Examples include /dev/tty.usbserial or /dev/ttyUSB0.'),

        Option(['-b', '--baudrate'],
               type=baudrate,
               default=115200,
               help='The baudrate of the serial port. The default is 115200.'),

        Option(['-c', '--exit-char'],
               type=exit_char,
               default='\x1d',
               help='The exit character (A to Z, [, \, ], or _) where Ctrl+<value> is used to exit. The default is ].')
    )

    try:
        parser.parse()

        com = Nanocom(serial.serial_for_url(parser.port, parser.baudrate),
                      exit_character=parser.exit_char)

        eprint('*** nanocom started ***')
        eprint('*** Ctrl+{} to exit  ***'.format(key_to_description(com.exit_character)))

        com.start()
        try:
            com.join()
        except KeyboardInterrupt:
            pass
        com.close()

        eprint('\n*** nanocom exited  *** ')

    except ParserError as e:
        eprint('Error: {}'.format(e))
        sys.exit(1)

    except ParserExitWithMessage as e:
        eprint(e)
        sys.exit(0)
