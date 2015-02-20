import os
from setuptools import setup, find_packages
import pyramid_orb

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except IOError:
    README = pyramid_orb.__doc__

try:
    VERSION = pyramid_orb.__version__ + '.{0}'.format(pyramid_orb.__revision__)
except AttributeError:
    VERSION = '1.0.0'
try:
    REQUIREMENTS = pyramid_orb.__depends__
except AttributeError:
    REQUIREMENTS = []

setup(
    name = 'pyramid-orb',
    version = VERSION,
    author = 'Eric Hulser',
    author_email = 'eric.hulser@gmail.com',
    maintainer = 'Eric Hulser',
    maintainer_email = 'eric.hulser@gmail.com',
    description = 'Bindings for the pyramid webframework and the ORB database ORM library.',
    license = 'LGPL',
    keywords = '',
    url = 'https://github.com/ProjexSoftware/pyramid_orb',
    include_package_data=True,
    packages = find_packages(),
    install_requires = REQUIREMENTS,
    tests_require = REQUIREMENTS,
    long_description= README,
    classifiers=[],
)
