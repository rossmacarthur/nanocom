# nanocom

[![PyPI](https://img.shields.io/pypi/v/nanocom)](https://pypi.org/project/nanocom/)
![PyPI: supported Python](https://img.shields.io/pypi/pyversions/nanocom)
[![Build status](https://img.shields.io/github/workflow/status/rossmacarthur/nanocom/build)](https://github.com/rossmacarthur/nanocom/actions?query=workflow%3Abuild)
[![Code style](https://img.shields.io/badge/code%20style-black-101010.svg)](https://github.com/psf/black)

An ultra simple command line serial client.

## Getting started

Install it using

```sh
pip install nanocom
```

and connect to your serial port using


```sh
nanocom --port /dev/ttyUSB0 --baudrate 115200
```

## Usage

Running `nanocom --help` will display all the cli options. The following options
are available

**-p, --port**

The path to the serial port. On macOS it will be something like
`/dev/tty.usbserial` and on Linux probably something like `/dev/ttyUSB0`. This
option is required.

**-b, --baudrate**

The baudrate of the serial port. This is typically something like `9600` or
`115200` but any integer is accepted. If not given, this option defaults to
`115200`.

**-m, --map**

A character map, `key`, `value` pair, such that when the `key` character is
entered into the client the `value` string will be sent instead. The `value`
string can be multiple characters and multiple character maps are allowed. An
example would be if you wanted to send a carriage return and a new line when a
new line character was given you would use `--map "\n" "\r\n"`.

**-c, --exit-char**

The exit character where the Ctrl key and this character are used to exit the
client. The character must be one of `A` to `Z`, `[`, `\`, `]`, or `_`. For
example if you gave the option `--exit-char \\` then the client would exit when
you pressed Ctrl + `\`.

## License

This project is licensed under the MIT license ([LICENSE](LICENSE) or
http://opensource.org/licenses/MIT).
