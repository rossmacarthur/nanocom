import sys

import click
import serial

import nanocom


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def key_to_description(character):
    return chr(ord('@') + ord(character))


def description_to_key(character):
    if not 64 <= ord(character) <= 95:
        raise ValueError()
    return chr(ord(character) - ord('@'))


class CharacterMap(click.Tuple):
    name = 'key value'

    def __init__(self):
        super().__init__((str, str))

    def convert(self, value, param, ctx):
        key, value = value
        if len(key) != 1:
            self.fail('KEY must be a single character')
        return (key, value)


class ExitCharacter(click.ParamType):
    name = 'char'

    def convert(self, value, param, ctx):
        try:
            return description_to_key(value.upper())
        except ValueError:
            self.fail(f'{value!r} is not a valid exit character', param, ctx)


@click.command(context_settings={'help_option_names': ['-h', '--help']},)
@click.version_option(
    nanocom.__version__, '-V', '--version', message='%(prog)s %(version)s',
)
@click.option(
    '-p',
    '--port',
    type=click.Path(exists=True),
    required=True,
    help='The serial port. E.g. /dev/tty.usbserial or /dev/ttyUSB0.',
)
@click.option(
    '-b',
    '--baudrate',
    default=115200,
    help='The baudrate of the serial port.',
    show_default=True,
)
@click.option(
    '-m',
    '--map',
    nargs=2,
    multiple=True,
    type=CharacterMap(),
    help='A character map where a string VALUE is sent for a character KEY.',
)
@click.option(
    '-c',
    '--exit-char',
    default='\\',
    type=ExitCharacter(),
    help='The exit character (a to z, [, \\, ], or _) where Ctrl+CHAR is used to exit.',
    show_default=True,
)
def cli(port, baudrate, map, exit_char):
    """
    \b
     _ __   __ _ _ __   ___   ___ ___  _ __ ___
    | '_ \\ / _` | '_ \\ / _ \\ / __/ _ \\| '_ ` _ \\
    | | | | (_| | | | | (_) | (_| (_) | | | | | |
    |_| |_|\\__,_|_| |_|\\___/ \\___\\___/|_| |_| |_|

    Ultra simple command line serial client.
    """
    com = nanocom.Nanocom(
        serial.serial_for_url(port, baudrate),
        exit_character=exit_char,
        character_map=map,
    )
    eprint('*** nanocom started ***')
    eprint('*** Ctrl+{} to exit  ***'.format(key_to_description(com.exit_character)))
    com.start()
    try:
        com.join()
    except KeyboardInterrupt:
        pass
    com.close()

    eprint('\n*** nanocom exited  *** ')


if __name__ == '__main__':
    cli.main(prog_name=nanocom.__title__)
