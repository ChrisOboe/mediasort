#!/usr/bin/env python2
#
# autosort post-processing script.
#
# Copyright (C) 2016 Chris Oboe <chrisoboe²eml.cc>
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
#


##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Sort movies and tv shows.
#
# This is a script for downloaded TV shows and movies. It uses scene-standard
# naming conventions to match TV shows and movies and get the metadata from
# tmdb.org to rename/move/sort/organize them as you like.
#
# The script relies on python library "guessit" (http://guessit.readthedocs.org)
# to extract information from file names and the library "tmdbsimple" to get 
# the metadata from tmdb.org. This script contains code from the nzbget videosort
# script
#
# Info about pp-script:
# Author: Chris Oboe (chrisoboe@eml.cc).
# Web-site: https://git.smackmack.industries/ChrisOboe/autosort.
# License: GPLv3 (http://www.gnu.org/licenses/gpl.html).
# PP-Script Version: 0.1.
#
# NOTE: This script requires Python 2.x to be installed on your system.

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################

import sys
import os
from guessit import guessit

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

# Check if the script is called from nzbget 11.0 or later
if not 'NZBOP_SCRIPTDIR' in os.environ:
	print('*** NZBGet post-processing script ***')
	print('This script is supposed to be called from nzbget (11.0 or later).')
	sys.exit(POSTPROCESS_ERROR)

# Check if directory still exist (for post-process again)
if not os.path.exists(os.environ['NZBPP_DIRECTORY']):
	print('[INFO] Destination directory %s doesn\'t exist, exiting' % os.environ['NZBPP_DIRECTORY'])
	sys.exit(POSTPROCESS_NONE)

# Check par and unpack status for errors
if os.environ['NZBPP_PARSTATUS'] == '1' or os.environ['NZBPP_PARSTATUS'] == '4' or os.environ['NZBPP_UNPACKSTATUS'] == '1':
	print('[WARNING] Download of "%s" has failed, exiting' % (os.environ['NZBPP_NZBNAME']))
	sys.exit(POSTPROCESS_NONE)

nzb_name=os.environ['NZBPP_NZBNAME']
download_dir=os.environ['NZBPP_DIRECTORY']

video_extensions=['.mkv','.avi']
min_size=100

# Process all the files in download_dir and its subdirectories
video_files = []

for root, dirs, files in os.walk(download_dir):
	for filename in files:
		filepath = os.path.join(root, filename)

		# Check extension
		ext = os.path.splitext(filename)[1].lower()
		if ext not in video_extensions: continue

		# Check minimum file size
		if os.path.getsize(filepath) < min_size: continue

		# Now we have out video file
		video_files.append(filepath)
