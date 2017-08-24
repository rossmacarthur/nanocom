import io
import os
import re
from setuptools import setup


def read(*path):
    """
    Python 2/3 file reading.
    """
    version_file = os.path.join(os.path.dirname(__file__), *path)
    with io.open(version_file, encoding='utf8') as f:
        return f.read()


def find_version():
    """
    Regex search __init__.py so that we do not have to import.
    """
    text = read('nanocom', '__init__.py')
    match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', text, re.M)
    if match:
        return match.group(1)
    raise RuntimeError('Unable to find version string.')


version = find_version()

long_description = read('README.rst')

install_requires = [
    'pyserial==3.4'
]

entry_points = {
    'console_scripts': [
        'nanocom=nanocom.__main__:cli'
    ]
}

setup(
    name='nanocom',
    packages=['nanocom'],
    version=version,
    install_requires=install_requires,
    entry_points=entry_points,
    description='An ultra simple serial client using pyserial.',
    long_description=long_description,
    author='Ross MacArthur',
    author_email='macarthur.ross@gmail.com',
    license='MIT',
    url='https://github.com/rossmacarthur/nanocom',
    download_url='https://github.com/rossmacarthur/nanocom/archive/{}.tar.gz'.format(version),
    keywords='serial client pyserial',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
