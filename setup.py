#!/usr/bin/env python

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='mediasort',
    version='0.7.1',
    author='Chris Oboe',
    author_email='chrisoboe@eml.cc',
    description='A library for automaticly sorting movies and episodes',
    license='GPLv3+',
    url='https://github.com/ChrisOboe/mediasort',
    download_url='https://github.com/ChrisOboe/mediasort/archive/v0.7.1.tar.gz',
    packages=['mediasort'],
    install_requires=[
        'python-dateutil',
        'tmdbsimple',
        'guessit>=2',
        'Mako',
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
)
