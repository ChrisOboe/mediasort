#!/usr/bin/env python2
#
# autosort script.
#
# Copyright (C) 2016 Chris Oboe <chrisoboe@eml.cc>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import ConfigParser
import os
import shutil
import datetime
import dateutil
import json
from guessit import guessit
import tmdbsimple as tmdb

tmdb.API_KEY = "bd65f46c799046c2d4286966d76c37c6"
video_extensions=['.mkv', '.avi']
tmdb_cache = os.path.expanduser('~') + '/.cache/autosort.tmdb'

# parse arguments via argparse
parser = argparse.ArgumentParser(
        description='Scrapes metadata for movies and episodes from TMDb '
        'by guessing the title from scene standard naming conventions. '
        'This product uses the TMDb API but is not endorsed or certified by TMDb.')
parser.add_argument("source",
        help="either a file that should be sorted, or a folder "
        "where every found media files are recursively sorted")
parser.add_argument('-c','--config', required=True,
        help="the config file")

args = parser.parse_args()
config = ConfigParser.RawConfigParser()
config.read(args.config)

# default config parser doesn't support defaults as i want
def config_get(section, option, default):
    if config.has_option(section, option):
        return config.get(section, option)
    else:
        return default

setting = {
        'general':{
            'language':config_get('general','language', 'en-US'),
            'tmdb_config_cache_days':config_get('general','tmdb_config_cache_days', '7')
            'simulate':config_get('general','simulate', 'yes')
            },
        'movies':{
            'destination':config_get('movies','destination', '/var/lib/media/movies/%t (%y)/%t (%y)')
            },
        'episodes':{
            'destination':config_get('episodes','destination', '/var/lib/media/series/%n (%y)/Season %s/S%sE%e - %t')
            }
        }

# downloads and caches the tmdb config
def download_tmdb_config():
    print("Downloading TMDb config")
    tmdb_config = tmdb.Configuration().info()
    tmdb_config['lastaccess'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(tmdb_cache, 'w') as cachefile:
        json.dump(tmdb_config, cachefile)
    return tmdb_config

# gets the tmdb config from cache if not too old
def get_tmdb_config():
    print("Getting TMDb config")
    # if cachefile doesnt exist download the data
    if not os.path.exists(tmdb_cache):
        print("Cachefile doesn't exist")
        return download_tmdb_config()

    # open cache
    with open(tmdb_cache, 'r') as cachefile:
        tmdb_config = json.load(cachefile)
    # check if too old
    lastaccess = dateutil.parser.parse(tmdb_config['lastaccess'])
    if (datetime.datetime.now() - lastaccess).days > setting['general']['tmdb_config_cache_days']:
        print("Cachefile exists, but is too old")
        return download_tmdb_config()
    else:
        print("Using config from cache")
        return tmdb_config

tmdb_config = get_tmdb_config()
tmdb_search = tmdb.Search()


def guess_vid(filename):
    print("Guessing {0}".format(filename))
    guess = guessit(filename)
    if guess['type'] == 'episode':
        print("Guessed type:    episode")
        print("Guessed title:   {0}".format(guess['title']))
        print("Guessed season:  {0}".format(guess['season']))
        print("Guessed episode: {0}".format(guess['episode']))
    elif guess['type'] == 'movie':
        print("Guessed type:  movie")
        print("Guessed title: {0}".format(guess['title']))
        if 'year' in guess: print("Guessed year:  {0}".format(guess['year']))
    else:
        print("Can't guess type.")
    return guess

def tmdb_movie(guess):
    print ("Searching TMDb for {0}".format(guess['title']))
    tmdb_args = {'query':guess['title'], 'include_adult':'true', 'language':setting['general']['language']}
    if 'year' in guess: tmdb_args['year']=guess['year']

    tmdb_search.movie(**tmdb_args)

    if not tmdb_search.results:
        print("Didn't found anything at TMDb.")
        return None

    if tmdb_search.total_results > 1:
        print("We found more than one possible movie for this name. We're going to use the first one.")
    else:
        print("We have exatly one match at TMDb. Bingo Bongo")

    return tmdb_search.results[0]

def get_movie_name(movie):
    newname = setting['movies']['destination']
    date = dateutil.parser.parse(movie['release_date'])
    replacement_rules = {
            '%t':movie['title'],
            '%ot':movie['original_title'],
            '%y':str(date.year)
    }
    for i in replacement_rules:
        newname = newname.replace(i, replacement_rules[i])
    return newname

def move(path, newname):
    filename, fileext = os.path.splitext(path)
    newpath = newname + fileext
    if setting['general']['simulate'] != 'yes' :
        print("Moving \"{0}\" to \"{1}\"".format(path,newpath))
        shutil.move(path, newpath)
    else:
        print("SIMULATE moving \"{0}\" to \"{1}\"".format(path,newpath))

def download_images(tmdb):
   return 

# get all files and write them to video_files
video_files = []
if os.path.exists(args.source):
    if os.path.isfile(args.source):
        ext = os.path.splitext(args.source)[1].lower()
        if ext in video_extensions:
            video_files.append(args.source)
    else:
        for root, dirs, files in os.walk(args.source):
            for filename in files:
                filepath = os.path.join(root, filename)
                ext = os.path.splitext(filename)[1].lower()
                if ext not in video_extensions: continue

                video_files.append(filepath)

# process files
for videofile in video_files:
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    guess = guess_vid(videofile_basename)

    if guess['type'] == 'episode':
        process_episode(guess)
    elif guess['type'] == 'movie':
        movie = tmdb_movie(guess)
        filename = get_movie_name(movie)
        move(videofile_abspath, filename)
        print movie
    else:
        continue

