"""
ORB stands for Object Relation Builder and is a powerful yet simple to use \
database class generator.
"""

# auto-generated version file from releasing
try:
    from ._version import __major__, __minor__, __revision__, __hash__
except ImportError:
    __major__ = 0
    __minor__ = 0
    __revision__ = 0
    __hash__ = ''

__version_info__ = (__major__, __minor__, __revision__)
__version__ = '{0}.{1}.{2}'.format(*__version_info__)

import orb
import projex

from . import utils


def register(config, modules=None, scope=None):
    scope = scope or {}
    if modules:
        # import the database models
        projex.importmodules(modules, silent=False)

    # expose all of the models to the API
    for name, model in orb.system.models().items():
        scope[name] = model

        if getattr(model, '__resource__', False):
            config.registry.rest_api.register(model)

def includeme(config):
    config.include('pyramid_restful')

    # define a new renderer for json
    settings = config.registry.settings

    # set the max limit when desired
    utils.DEFAULT_MAX_LIMIT = int(settings.pop('orb.settings.default_max_limit', utils.DEFAULT_MAX_LIMIT))

    # create the orb global settings
    for key, value in settings.items():
        if key.startswith('orb.settings'):
            sub_key = key.replace('orb.settings.', '')
            setattr(orb.system.settings(), sub_key, value)

    # create the database conneciton
    db_type = settings.get('orb.db.type')
    if db_type:
        db = orb.Database(db_type)
        db.setName(settings.get('orb.db.name'))
        db.setUsername(settings.get('orb.db.user'))
        db.setPassword(settings.get('orb.db.password'))
        db.setHost(settings.get('orb.db.host'))
        db.setPort(settings.get('orb.db.port'))
        try:
            db.setTimeout(eval(settings.get('orb.db.timeout')))
        except StandardError:
            pass
        db.activate()

        config.registry.db = db

    # create the API factory
    api_root = settings.get('orb.api.root')
    if api_root:
        from .api import OrbApiFactory

        api = OrbApiFactory(
            application=settings.get('orb.api.application', 'ORB'),
            version=settings.get('orb.api.version', '1.0.0')
        )

        permission = settings.get('orb.api.permission')
        api.serve(config, api_root, route_name='orb.api', permission=permission)

        # store the API instance on the configuration
        config.registry.rest_api = api