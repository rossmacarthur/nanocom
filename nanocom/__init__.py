from __future__ import unicode_literals
import atexit
import codecs
import fcntl
import sys
import termios
import threading


__version__ = '1.1.0'


try:
    chr = unichr
except NameError:
    pass


class Console(object):

    def __init__(self):
        if sys.version_info < (3, 0):
            self.byte_output = sys.stdout
            self.enc_stdin = codecs.getreader(sys.stdin.encoding)(sys.stdin)
        else:
            self.byte_output = sys.stdout.buffer
            self.enc_stdin = sys.stdin
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        atexit.register(self.cleanup)

    def setup(self):
        new = termios.tcgetattr(self.fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSANOW, new)

    def cleanup(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

    def getkey(self):
        c = self.enc_stdin.read(1)
        if c == chr(0x7f):
            c = chr(8)
        return c

    def write_bytes(self, byte_string):
        self.byte_output.write(byte_string)
        self.byte_output.flush()

    def cancel(self):
        fcntl.ioctl(self.fd, termios.TIOCSTI, b'\0')


class Nanocom(object):

    def __init__(self, serial_instance, exit_character='\x1d', character_map=None):
        self.console = Console()
        self.serial = serial_instance
        self.exit_character = exit_character
        self.character_map = character_map
        self.rx_decoder = codecs.getincrementaldecoder('UTF-8')('replace')
        self.tx_encoder = codecs.getincrementalencoder('UTF-8')('replace')

    def start(self):
        self.alive = True
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()
        self.transmitter_thread = threading.Thread(target=self.writer, name='tx')
        self.transmitter_thread.daemon = True
        self.transmitter_thread.start()
        self.console.setup()

    def stop(self):
        self.alive = False

    def join(self):
        self.transmitter_thread.join()
        self.serial.cancel_read()
        self.receiver_thread.join()

    def close(self):
        self.serial.close()

    def reader(self):
        try:
            while self.alive:
                data = self.serial.read(self.serial.in_waiting or 1)
                if data:
                    self.console.write_bytes(data)
        except Exception:
            self.alive = False
            self.console.cancel()
            raise

    def writer(self):
        try:
            while self.alive:
                try:
                    c = self.console.getkey()
                except KeyboardInterrupt:
                    c = '\x03'  # Ctrl+C
                if not self.alive:
                    break
                if c == self.exit_character:
                    self.stop()
                    break
                elif self.character_map and c in self.character_map:
                    self.serial.write(self.tx_encoder.encode(self.character_map[c]))
                else:
                    self.serial.write(self.tx_encoder.encode(c))
        except Exception:
            self.alive = False
            raise
