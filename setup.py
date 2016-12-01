#!/usr/bin/env python

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='mediasort',
    version='0.2.0',
    author='Chris Oboe',
    author_email='chrisoboe@eml.cc',
    description='A tool for automaticly sorting movies and episodes',
    license='GPLv3+',
    url='https://git.smackmack.industries/ChrisOboe/MediaSort',
    download_url='https://git.smackmack.industries/ChrisOboe/MediaSort/archive/v0.2.0.tar.gz',
    packages=['mediasort'],
    install_requires=[
        'python-dateutil',
        'tmdbsimple',
        'guessit'
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
    ],
)
