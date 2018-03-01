from __future__ import print_function, unicode_literals
import os
import serial
import sys
from nanocom import __version__, Nanocom


class ParserExitWithMessage(Exception):
    pass


class ParserError(Exception):
    pass


class OptionType(object):

    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        if not hasattr(self, 'help_name'):
            self.help_name = self.name.upper()

    def __call__(self, *args):
        raise NotImplemented()


class Option(object):

    def __init__(self, identifiers, default=None, exit=None, help='', is_flag=None, type=None, args=1, multiple=False,
                 required=True):
        self.name = max(identifiers, key=len).lstrip('-').replace('-', '_')
        self.identifiers = sorted(identifiers, key=len)
        self.default = default
        self.exit = exit
        self.help = help
        self.is_flag = type is None
        self.type = type
        self.args = args
        self.multiple = multiple
        self.required = required

    @property
    def help_text(self):
        prefix = ', '.join(self.identifiers)
        if self.type:
            prefix += ' ' + self.type.help_name
        return (prefix, self.help)

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
        helps += [option.help_text for option in self.options]
        col = len(max((h[0] for h in helps), key=len))
        usage = 'Usage: {prog} [OPTIONS]'
        option_list = '\n'.join('  {:<{col}}  {}'.format(*h, col=col) for h in helps)
        return usage + help_prefix + '\nOptions:\n' + option_list

    def parse_id(self, option):
        if option.is_flag:
            if option.exit:
                raise ParserExitWithMessage(option.exit.format(**self.help_format))
            else:
                return True
        elif len(self.args[:option.args]) != option.args or \
                any(arg.startswith('-') for arg in self.args[:option.args]):
            message = '{} requires {} argument'.format(option, option.args)
            if option.args > 1:
                message += 's'
            raise ParserError(message)

        value, self.args = self.args[:option.args], self.args[option.args:]

        try:
            return option.type(*value)
        except (TypeError, ValueError):
            raise ParserError('invalid value for {}: {} is not a valid {}'.format(
                option, ' '.join(value), option.type.name.lower(),))

    def parse(self):
        # loop through args and collect values
        while self.args:
            arg = self.args.pop(0)
            if arg.startswith('-'):
                for option in self.options:
                    if arg in option.identifiers:
                        parsed = self.parse_id(option)
                        if hasattr(self, option.name):
                            if option.multiple:
                                getattr(self, option.name).append(parsed)
                            else:
                                raise ParserError('received multiple of option {}'.format(arg))
                        elif option.multiple:
                            setattr(self, option.name, [parsed])
                        else:
                            setattr(self, option.name, parsed)
                        break
                else:
                    raise ParserError('unrecognised option {}'.format(arg))
            else:
                raise ParserError('unexpected argument {}'.format(arg))

        # check all values have been set else set defaults or raise error
        for option in self.options:
            if not hasattr(self, option.name) and not option.is_flag:
                if not option.default and option.required:
                    raise ParserError('{} is required'.format(option))
                else:
                    setattr(self, option.name, option.default)


class Path(OptionType):

    def __call__(self, arg):
        if os.path.exists(arg):
            return arg
        raise ValueError()


class Integer(OptionType):

    def __call__(self, arg):
        return int(arg)


class ExitCharacter(OptionType):
    name = 'Exit Character'
    help_name = 'CHAR'

    def __call__(self, arg):
        return description_to_key(arg)


class CharacterMap(OptionType):
    name = 'Character Map'
    help_name = 'KEY VALUE'

    def __call__(self, *args):
        if len(args) != 2 or len(args[0]) != 1:
            raise ValueError()
        return args


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def key_to_description(character):
    return chr(ord('@') + ord(character))


def description_to_key(character):
    if not 64 <= ord(character) <= 95:
        raise ValueError()
    return chr(ord(character) - ord('@'))


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
               exit='{prog} ' + __version__,
               help='Show the version and exit.'),

        Option(['-p', '--port'],
               type=Path(),
               help='The serial port. Examples include /dev/tty.usbserial or /dev/ttyUSB0.'),

        Option(['-b', '--baudrate'],
               type=Integer(),
               default=115200,
               help='The baudrate of the serial port. The default is 115200.'),

        Option(['-m', '--map'],
               type=CharacterMap(),
               args=2,
               multiple=True,
               required=False,
               help='A character map where a string VALUE is sent for a character KEY. Multiple maps are allowed.'),

        Option(['-c', '--exit-char'],
               type=ExitCharacter(),
               default='\x1d',
               help='The exit character (A to Z, [, \, ], or _) where Ctrl+CHAR is used to exit. The default is ].')
    )

    try:
        parser.parse()

        character_map = None
        if parser.map:
            character_map = dict(parser.map)

        com = Nanocom(serial.serial_for_url(parser.port, parser.baudrate),
                      exit_character=parser.exit_char, character_map=character_map)

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
