# Copyright (C) 2016-2017  Oboe, Chris <chrisoboe@eml.cc>
# Author: Oboe, Chris <chrisoboe@eml.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" initializes mediasort and its plugins """

from mediasort.enums import PluginType, MediaType, MetadataType, ImageType
from mediasort import error


def check_function(module, function):
    """ check if a module contains the functions from functionlist """
    if not hasattr(module, function):
        raise error.InvalidPlugin("Plugin {0} is missing {1}".format(
            module.__name__,
            function))


def load_module(name, config):
    # check if module is already loaded
    modulename = 'mediasort.plugins' + '.' + name
    if modulename in sys.modules:
        return sys.modules[modulename]

    path = '{0}/plugins/{1}.py'.format(
        os.path.dirname(os.path.abspath(__file__)),
        name)

    # check if module exists
    if not os.path.isfile(path):
        print("The module {0} doesn't exist in the plugin folder".format(name))
        sys.exit(1)

    module = import_module(modulename)
    check_function(module, 'init')

    module.init(config)
    return module


def initialize_plugins(config):
    """
    Calls the init function of every plugin
    checks if the plugins has the needed functions
    checks if some configurations are valid
    """

    plugins = {
        PluginType.guess: [],
        PluginType.identificator: {
            MediaType.movie: {
                'modules': [],
                'ids': [],
            },
            MediaType.episode: {
                'modules': [],
                'ids': [],
            },
        },
        PluginType.metadata: {
            MediaType.movie: {
                MetadataType.title: [],
                MetadataType.originaltitle: [],
                MetadataType.premiered: [],
                MetadataType.tagline: [],
                MetadataType.plot: [],
                MetadataType.set: [],
                MetadataType.certification: [],
                MetadataType.rating: [],
                MetadataType.votes: [],
                MetadataType.studios: [],
                MetadataType.countries: [],
                MetadataType.genres: [],
                MetadataType.directors: [],
                MetadataType.scriptwriters: [],
                MetadataType.actors: [],
            },
            MediaType.tvshow: {
                MetadataType.title: [],
                MetadataType.premiered: [],
                MetadataType.plot: [],
                MetadataType.certification: [],
                MetadataType.rating: [],
                MetadataType.votes: [],
                MetadataType.studios: [],
                MetadataType.genres: [],
                MetadataType.actors: [],
            },
            MediaType.episode: {
                MetadataType.title: [],
                MetadataType.showtitle: [],
                MetadataType.plot: [],
                MetadataType.premiered: [],
                MetadataType.rating: [],
                MetadataType.votes: [],
            },
        },
        PluginType.images: {
            MediaType.movie: {
                ImageType.poster: [],
                ImageType.background: [],
                ImageType.disc: [],
                ImageType.banner: [],
                ImageType.logo: [],
                ImageType.clearart: [],
                ImageType.art: [],
            },
            MediaType.tvshow: {
                ImageType.poster: [],
                ImageType.background: [],
                ImageType.banner: [],
                ImageType.logo: [],
                ImageType.clearart: [],
                ImageType.charart: [],
                ImageType.art: [],
            },
            MediaType.season: {
                ImageType.poster: [],
            },
            MediaType.episode: {
                ImageType.thumbnail: [],
            },
        },
    }

    # initializing and function existance checking

    for plugintype in config['plugins']:
        if plugintype == PluginType.guess:
            for plugin in config['plugins'][category]:
                # load the module
                module = load_module(plugin, config[plugin])
                # check needed functions
                check_function(module, 'get_guess')
                # add module to dict
                plugins[category].append(module)

        elif plugintype == PluginType.identificator:
            for mediatype in config['plugins'][category]:
                for plugin in config['plugins'][category][mediatype]:
                    # load the module
                    module = load_module(plugin, config[plugin])
                    # check needed functions
                    check_function(module, 'get_identificator_list')
                    check_function(module, 'get_identificator')
                    # add module to dict
                    plugins[category][mediatype]['modules'].append(module)
                    plugins[category][mediatype]['ids'].extend(
                        module.get_identificator_list())

        elif plugintype == PluginType.metadata:
            for mediatype in config['plugins'][category]:
                for metadatatype in config['plugins'][category][mediatype]:
                    for plugin in config['plugins'][category][mediatype][metadatatype]:
                        # load the module
                        module = load_module(plugin, config[plugin])
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_metadata')
                        # add module to dict
                        plugins[category][mediatype][metadatatype].append(module)

        elif plugintype == PluginType.image:
            for mediatype in config['plugins'][category]:
                for imagetype in config['plugins'][category][mediatype]:
                    for plugin in config['plugins'][category][mediatype][imagetype]:
                        # load the module
                        module = load_module(plugin, config[plugin])
                        # check needed functions
                        check_function(module, 'get_needed_ids')
                        check_function(module, 'get_image')
                        # add module to dict
                        plugins[category][mediatype][imagetype].append(module)

    # since the pluginlist is built, we can now do some checks
    for mediatype in plugins[PluginType.metadata]:
        for metadatatype in plugins[PluginType.metadata][mediatype]:
            plugin = plugins[PluginType.metadata][mediatype][metadatatype]
            ids = plugins[PluginType.identificator][mediatype]['ids']
            # check if we have the ids that are needed by the selected plugins
            if not plugin.get_needed_ids().issubsetof(ids):
                raise error.InvalidConfig()

    return plugins


def sort(videofile, config):
    """ sorts a videofile """
    videofile_basename = os.path.basename(videofile)
    videofile_abspath = os.path.abspath(videofile)
    videofile_extension = os.path.splitext(videofile_basename)[1].lower()[1:]

    print("\nProcessing \"{0}\"".format(videofile_abspath))

    try:
        guess = get_guess(videofile_abspath, config)
        identificator = get_identificator(guess, config)
        if identificator['type'] == MediaType.episode:
            tvshow_identificator = identificator.copy()
            tvshow_identificator['type'] = MediaType.tvshow
            tvshow_identificator['episode'] = None
            tvshow_identificator['season'] = None
            season_identificator = identificator.copy()
            season_identificator['type'] = MediaType.season
            season_identificator['episode'] = None
            tvshow_metadata = get_metadata(tvshow_identificator, config)
            tvshow_images = get_images(tvshow_identificator, config)
            season_images = get_images(season_identificator, config)
        metadata = get_metadata(identificator, config)
        images = get_images(identificator, config)
    except NotEnoughData as err:
        print(err)
        print("Skipping this file")
        return

    # set replacement rules
    if identificator['type'] == MediaType.movie:
        replacers = {
            '$t': helpers.filter_fs_chars(metadata['title']),
            '$ot': helpers.filter_fs_chars(metadata['originaltitle']),
            '$y': str(dateutil.parser.parse(metadata['premiered']).year),
        }
    elif identificator['type'] == MediaType.episode:
        replacers = {
            '$tt': helpers.filter_fs_chars(tvshow_metadata['title']),
            '$y': str(dateutil.parser.parse(tvshow_metadata['premiered']).year),
            '$et': helpers.filter_fs_chars(metadata['title']),
            '$sn': str(identificator['season']).zfill(2),
            '$en': str(identificator['episode']).zfill(2),
        }

    # check if movie destination already exists
    video_dst = helpers.replace_by_rule(
        replacers,
        config['paths'][identificator['type']]['base_path']
        + config['paths'][identificator['type']]['videofile'])

    if os.path.exists(video_dst) and config['general']['overwrite_videos']:
        print("Videofile already exists")
        print("Skipping this file")
        return

    # download images
    def download_images(identificator, images):
        for image in images:
            image_dst = helpers.replace_by_rule(
                replacers,
                config['paths'][identificator['type']][image])
            if (not os.paths.exists(image_dst)
               or config['general']['overwrite_images']):
                helpers.download(images[image], image_dst)

    download_images(identificator, images)
    if identificator['type'] == MediaType.episode:
        download_images(tvshow_identificator, tvshow_images)
        download_images(season_identificator, season_images)

    # write nfo
        nfo.write_movie_nfo(
            movie=movie,
            dst=helpers.replace_by_rule(replacers,
                                        settings['movie']['base_path']
                                        + settings['movie']['nfo_path']),
            rating_country=settings['general']['languages'][0],
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos']
        )

    elif guess['type'] == MediaType.episode:
        tvshow = tmdb.get_tvshow_info(
            guess["ids"],
            settings['general']['languages'])

        episode = tmdb.get_episode_info(guess['ids'],
                                        guess['season'],
                                        guess['episode'],
                                        settings['general']['languages'])

        replacers = {
            '$st': helpers.filter_fs_chars(tvshow['name']),
            '$sot': helpers.filter_fs_chars(tvshow['original_name']),
            '$y': str(dateutil.parser.parse(tvshow['first_air_date']).year),
            '$et': helpers.filter_fs_chars(episode['name']),
            '$sn': str(episode['season_number']).zfill(2),
            '$en': str(episode['episode_number']).zfill(2),
            '$ext': videofile_extension
        }

        dst = (helpers.replace_by_rule(replacers,
                                       settings['tvshow']['base_path']
                                       + settings['episode']['episode_path']))
        if os.path.exists(dst) and settings['general']['overwrite_videos']:
            return

        downloads = [
            {"mediatype": MediaType.tvshow,
             "ids":   guess['ids'],
             "images": [
                 {"imagetype":   "poster",
                  "providers":   settings['tvshow']['poster_providers'],
                  "destination": settings['tvshow']['poster_path']},
                 {"imagetype":   "background",
                  "providers":   settings['tvshow']['background_providers'],
                  "destination": settings['tvshow']['background_path']},
                 {"imagetype":   "banner",
                  "providers":   settings['tvshow']['banner_providers'],
                  "destination": settings['tvshow']['banner_path']},
                 {"imagetype":   "logo",
                  "providers":   settings['tvshow']['logo_providers'],
                  "destination": settings['tvshow']['logo_path']},
                 {"imagetype":   "clearart",
                  "providers":   settings['tvshow']['clearart_providers'],
                  "destination": settings['tvshow']['clearart_path']},
                 {"imagetype":   "charart",
                  "providers":   settings['tvshow']['charart_providers'],
                  "destination": settings['tvshow']['charart_path']},
                 {"imagetype":   "art",
                  "providers":   settings['movie']['art_providers'],
                  "destination": settings['movie']['art_path']}]},
            {"mediatype": MediaType.season,
             "ids":       guess['ids'],
             "season":    episode['season_number'],
             "images": [
                 {"imagetype":   "poster",
                  "providers":   settings['season']['poster_providers'],
                  "destination": settings['season']['poster_path']}]},
            {"mediatype": MediaType.episode,
             "ids":       guess['ids'],
             "season":    episode['season_number'],
             "episode":   episode['episode_number'],
             "images": [
                 {"imagetype":   "thumbnail",
                  "providers":   settings['episode']['thumbnail_providers'],
                  "destination": settings['episode']['thumbnail_path']}]},
        ]

        # write series nfo
        nfo.write_tvshow_nfo(
            tvshow,
            settings['general']['languages'][0],
            helpers.replace_by_rule(replacers,
                                    settings['tvshow']['base_path']
                                    + settings['tvshow']['nfo_path']),
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos'])

        # write episode nfo
        nfo.write_episode_nfo(
            tvshow,
            episode,
            helpers.replace_by_rule(replacers,
                                    settings['tvshow']['base_path']
                                    + settings['episode']['nfo_path']),
            releasegroup=guess['releasegroup'],
            source=guess['source'],
            simulate=settings['debug']['simulate_nfo'],
            overwrite=settings['general']['overwrite_nfos']
        )

    else:
        return

    # download images
    for download in downloads:
        for image in download['images']:
            # check if special provider "None" is used
            if image["providers"][0] == "None":
                continue

            if download['mediatype'] == MediaType.movie:
                base_path = settings['movie']['base_path']
            else:
                base_path = settings['tvshow']['base_path']

            url = get_image_url(
                ids=download['ids'],
                image_type=image['imagetype'],
                media_type=download['mediatype'],
                languages=settings['general']['languages'],
                providers=image['providers'],
                season=None if 'season' not in download else download['season'],
                episode=None if 'episode' not in download else download['episode']
            )

            if url is not None:
                helpers.download(
                    src=url,
                    dst=helpers.replace_by_rule(
                        replacers,
                        base_path + image['destination']),
                    simulate=settings['debug']['simulate_images'],
                    overwrite=settings['general']['overwrite_images'])

    # move file
    helpers.move(videofile_abspath,
                 dst,
                 settings['debug']['simulate_move'],
                 settings['general']['overwrite_videos'])
        },
        'tvshow': {
            'tmdb': tmdb.get_tvshow_image,
            'fanarttv': fanarttv.get_tvshow_image,
        },
        'season': {
            'tmdb': tmdb.get_season_image,
        },
        'episode': {
            'tmdb': tmdb.get_episode_image,
        },
    },
}
