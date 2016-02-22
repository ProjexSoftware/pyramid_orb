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


def includeme(config):
    # define a new renderer for json
    config.add_renderer('json2', factory='pyramid_orb.renderer.json2_renderer_factory')

    settings = config.registry.settings

    # create the database conneciton
    db_type = settings.get('orb.db.type')
    if db_type:
        db = orb.Database(db_type)
        db.setName(settings.get('orb.db.name'))
        db.setUsername(settings.get('orb.db.user'))
        db.setPassword(settings.get('orb.db.password'))
        db.setHost(settings.get('orb.db.host'))
        db.setPort(settings.get('orb.db.port'))
        db.activate()
        db.connect()

        config.registry.db = db

    # create the orb global settings
    for key, value in settings.items():
        if key.startswith('orb.settings'):
            sub_key = key.replace('orb.settings.', '')
            setattr(orb.system.settings(), sub_key, value)

    # create the API factory
    api_root = settings.get('orb.api.root')

    if api_root:
        from .api import ApiFactory

        api = ApiFactory(version=settings.get('orb.api.version', '1.0.0'))
        api.serve(config, api_root, route_name='orb.api')

        # store the API instance on the configuration
        config.registry.api = api