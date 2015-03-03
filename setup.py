from setuptools import setup, find_packages
import pyramid_orb

setup(
    name='pyramid-orb',
    version=pyramid_orb.__version__,
    author='Eric Hulser',
    author_email='eric.hulser@gmail.com',
    maintainer='Eric Hulser',
    maintainer_email='eric.hulser@gmail.com',
    description='Bindings for the pyramid webframework and the ORB database ORM library.',
    license='LGPL',
    keywords='',
    url='https://github.com/ProjexSoftware/pyramid_orb',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'pyramid',
        'orb'
    ],
    tests_require=[],
    long_description='Bindings for the pyramid webframework and the ORB database ORM library.',
    classifiers=[],
)
