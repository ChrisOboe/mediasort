# MediaSort Readme
Autosort is a tool which can automaticly sort movies and episodes from scene releases.
It's written in python and uses the guessit library for guessing informations based on filename / foldername.
It then uses this informations to scrape the metadata from TMDb by using the tmdbsimple library.

## Usage
```
run.py [-h] [-v] [-c CONFIG] [-f type] source
```

### Arguments
| short | long | description |
| -------- | -------- | -------- | 
| -h | --help | shows help |
| -v | --verbose | be more verbose |
| -c | --config | the configfile to use. Defaults to xdg_config_home/mediasort/config.ini |
| -t | --force-type | force either "episode" or "movie" |

## Config file
A example config file looks like the following:
```
[debug]
# when simulation is on it doesn't write/move files
simulate_nfo = False
simulate_images = False
simulate_move = False

[general]
# The language for the TMDb scraping
language = EN-US
# The path where stuff is cached.
# At the moment only the general TMDb config is cached
cache_path = ~/.cache/autosort/
# allow or disallow overwriting of existing files
overwrite_nfos = True
overwrite_images = True
overwrite_videos = False

[videofiles]
# Only files which this extensions are used
allowed_extensions = avi mkv
# Only files bigger than this size in MB will be used
minimal_file_size = 100

[tmdb]
# The days the cache is valid.
tmdb_config_cache_days = 7
# The TMDb api key
tmdb_api_key =   bd65f46c799046c2d4286966d76c37c6
# if images should be downloaded via https
https_download = False
# The size of the poster
poster_size = w500
# The size of the backdrop / fanart
backdrop_size = w1280
# The size of the episode thumbnail
still_size = w300

[movie]
# A custom entry which can be accessed by %(entry_name)s
base_path = /var/lib/movies/$t ($y)
# The destination where the movies are moved
movie = %(base_path)s/$t ($y).$ext
# The destination where the nfo will be written to
nfo = %(base_path)s/$t ($y).nfo
# The destination where the backdrop will be downloaded
backdrop = %(base_path)s/fanart.jpg
# The destination where the poster will be downloaded
poster = %(base_path)s/poster.jpg

[tvshow]
base_path = /var/lib/series/$st ($y)
nfo = %(base_path)s/tvshow.nfo
poster = %(base_path)s/poster.jpg
backdrop = %(base_path)s/fanart.jpg
season_poster = %(base_path)s/season$sn-poster.jpg

[episode]
base_path = /var/lib/series/$st ($y)
episode = %(base_path)s/Season $sn/S$snE$en $et.$ext
nfo = %(base_path)s/Season $sn/S$snE$en $et.nfo
still = %(base_path)s/Season $sn/S$snE$en $et-thumb.jpg
```

The following special vars can be used in the movie destinations:

| Variable | Replacement |
| -------- | -------- | 
| $t | The title of the movie     |
| $ot | The original title of the movie |
| $y | The year of the movie |
| $ext | The file extension of the original file |

and the following ones can be used in the episode destinations:

| Variable | Replacement |
| -------- | -------- | 
| $st | The title of the series     |
| $sot | The original title of the series |
| $y | The first air date of the series |
| $et | The title of the episode |
| $sn | The season number |
| $en | The episode number |
| $ext | The file extension of the original file |

## known oddities
- when having movies in a folder with a number it is recognized as episode. so either force movies via commandline, or use folders without numbers.
- when having videos in subfolders, the subfolder with the most scene infos will get used. 
- tmdb has problems with surpressed apostrophes e.g. bobs burgers won't find anything, bob burgers or bob's burgers will work.


