from .factory import ApiFactory
from .service import Service, ClassService, ModuleService, RestCallable, ObjectService
from .collections import ModelService, CollectionService
from .resources import RecordService, PipedRecordResource


class expose(object):
    @staticmethod
    def get(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return RestCallable(name,
                                callable,
                                method='GET',
                                permit=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def post(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return RestCallable(name,
                                callable,
                                method='POST',
                                permit=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def delete(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return RestCallable(name,
                                callable,
                                method='DELETE',
                                permit=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def put(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return RestCallable(name,
                                callable,
                                method='PUT',
                                permit=options.pop('permission', '__DEFAULT__'))
        return setup

    @staticmethod
    def patch(**options):
        def setup(callable):
            name = options.pop('name', callable.__name__)
            return RestCallable(name,
                                callable,
                                method='PATCH',
                                permit=options.pop('permission', '__DEFAULT__'))
        return setup