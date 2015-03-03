#!/usr/bin/python

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

# maintanence information
__maintainer__ = 'Projex Software'
__email__ = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

# define version information (major,minor,maintanence)
__depends__ = []
__major__ = 1
__minor__ = 1
__revision__ = 11

__version_info__ = (__major__, __minor__, __revision__)
__version__ = '%s.%s' % (__major__, __minor__)

def includeme(config):
    config.add_renderer('json2', factory='pyramid_orb.renderer.json2_renderer_factory')