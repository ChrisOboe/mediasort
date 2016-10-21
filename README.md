# Autosort Readme
## Usage
```
autosort.py [-h] -c CONFIG source
```
- CONFIG has to be a valid config file for autosort
- source can be a video file or a folder which will be recursivly searched

## How the software works
The movie title is guessed from the filename. 
TMDb will be searched by this name. The first result will be used.
The metadata, the backdrop and the poster image will be downloaded from TMDb.
The file will be moved.
All the paths are configurable

## Config file
A example config file looks like the following:
```
[general]
# The language for the TMDb scraping
language = EN-US
# The path where stuff is cached. At the moment only the general TMDb config is cached
cache_path = ~/.cache/autosort/
# The days the cache is valid.
tmdb_config_cache_days = 7
# If specific actions should be simulated. Usefull if you don't trust this software (And you shouldn't, it isn't tested very much)
simulate_move = yes
simulate_download = yes
simulate_nfo = yes
# The TMDb api key
tmdb_api_key =   bd65f46c799046c2d4286966d76c37c6
# Only files which this extensions are used
allowed_extensions = avi mkv
# Only files bigger than this size in MB will be used
minimal_file_size = 100

[movie]
# A custom entry which can be accessed by %(entry_name)s
base_path = /var/lib/movies/$t ($y)
# The destination where the movies are moved
video_destination = %(base_path)s/$t ($y).$ext
# The destination where the nfo will be written to
nfo_destination = %(base_path)s/$t ($y).nfo
# The destination where the backdrop will be downloaded
backdrop_destination = %(base_path)s/fanart.jpg
# The destination where the poster will be downloaded
poster_destination = %(base_path)s/poster.jpg
```

The following special vars can be used in the movie destinations:
| Variable | Replacement |
| -------- | -------- | 
| $t | The title of the movie     |
| $ot | The original title of the movie |
| $y | The year of the movie |
| $ext | The file extension of the original file |