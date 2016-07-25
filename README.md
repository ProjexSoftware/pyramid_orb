pyramid_orb
======================

The `pyramid_orb` project is aimed at providing an integration layer between the
ORB database mapping system and the pyramid web framework.

Installation
-----------------------

    pip install pyramid_orb

Documentation
-----------------------

Documentation is a part of the global ORB framework docs, hosted on GitBook.com.

For specific ORB-Pyramid integration, [refer to this section on pyramid_orb](https://orb-framework.gitbooks.io/orb/content/integrations/pyramid.html).

Testing
-----------------------

To run the unit tests you will need to create a virtual environment, install
the test requirements, and execute the py test command:

    virtualenv env
    source env/bin/activate
    pip install -r requirements-test.txt
    py.test tests
