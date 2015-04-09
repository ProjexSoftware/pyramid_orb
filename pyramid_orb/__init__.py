"""
ORB stands for Object Relation Builder and is a powerful yet simple to use \
database class generator.
"""

# define authorship information
__authors__ = ['Eric Hulser']
__author__ = ','.join(__authors__)
__credits__ = []
__copyright__ = 'Copyright (c) 2011, Projex Software'
__license__ = 'LGPL'

# maintenance information
__maintainer__ = 'Eric Hulser'
__email__ = 'eric.hulser@gmail.com'

# define version information (major,minor,revision)
__depends__ = []
__major__ = 1
__minor__ = 1
__revision__ = 20

__version_info__ = (__major__, __minor__, __revision__)
__version__ = '%s.%s.%s' % __version_info__


def includeme(config):
    # define a new renderer for json
    config.add_renderer('json2', factory='pyramid_orb.renderer.json2_renderer_factory')