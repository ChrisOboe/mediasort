#!/usr/bin/env python

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='mediasort',
      version='0.1.0',
      description='A tool for automaticly sorting movies and episodes',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3.5',
      ]
      author='Chris Oboe'.
      author_email='chrisoboe@eml.cc',
      license='GPLv3+',
      packages=['mediasort'],
      install_requires=[
          'python-dateutil',
          'tmdbsimple',
          'guessit'
      ],
      include_package_data=True,
      zip_safe=False,
      url='https://git.smackmack.industries/ChrisOboe/MediaSort')
      
