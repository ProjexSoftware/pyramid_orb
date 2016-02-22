import re

from .abstract import AbstractService
from .restful import RestfulService
from pydoc import render_doc
from pyramid.httpexceptions import HTTPBadRequest


class CallableService(object):
    def __init__(self, name, callable, method='GET', permit=None):
        self.__name__ = name
        self.__callable__ = callable
        self.__method__ = method
        self.__permit__ = permit

    def __call__(self, request):
        if self.__method__ == request.method:
            return self.__callable__(request)
        else:
            raise HTTPBadRequest()

    def get(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return CallableService(name, callable, 'GET', permit)
        return setup

    def post(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return CallableService(name, callable, 'POST', permit)
        return setup

    def delete(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return CallableService(name, callable, 'DELETE', permit)
        return setup

    def put(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return CallableService(name, callable, 'PUT', permit)
        return setup

    def patch(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return CallableService(name, callable, 'PATCH', permit)
        return setup

class ModuleService(AbstractService):
    def __init__(self, request, module, parent=None, name=None):
        super(ModuleService, self).__init__(request, name or module.__name__.split('.')[-1], parent)

        self.module = module
        self.callables = {}
        for callable in vars(module).values():
            if isinstance(callable, CallableService):
                self.callables.setdefault(callable.__name__, {})
                self.callables[callable.__name__][callable.__method__] = callable

    def __getitem__(self, key):
        if key in self.callables:
            return self
        else:
            raise KeyError(key)

    def process(self):
        name = self.request.path.strip('/').split('/')[-1]
        try:
            callable = self.callables[name][self.request.method]
        except KeyError:
            raise HTTPBadRequest()
        else:
            # check to see if we're looking for help
            if 'help' in self.request.params:
                docgen = getattr(callable.__callable__, 'help', None)
                if docgen:
                    return {'message': docgen(self.request)}
                else:
                    return {'message': re.sub('\w\x08', '', render_doc(callable.__callable__))}

            return callable(self.request)

    def permit(self):
        name = self.request.path.strip('/').split('/')[-1]
        try:
            callable = self.callables[name][self.request.method]
        except KeyError:
            return None
        else:
            default = super(ModuleService, self).permit()
            return callable.__permit__ if callable.__permit__ != '__DEFAULT__' else default


class ClassService(AbstractService):
    def __init__(self, request, cls, parent=None, name=None):
        super(ClassService, self).__init__(request, name or cls.__name__, parent)

        self.instance = cls(request)
        self.callables = {}
        for callable in vars(self.instance).values():
            if isinstance(callable, RestfulService):
                self.callables.setdefault(callable.__name__, {})
                self.callables[callable.__name__][callable.__method__] = callable

    def __getitem__(self, key):
        if key in self.callables:
            return self
        else:
            raise KeyError(key)

    def process(self):
        name = self.request.path.split('/')[-1]
        try:
            callable = self.callables[name][self.request.method]
        except KeyError:
            raise HTTPBadRequest()
        else:
            # check to see if we're looking for help
            if 'help' in self.request.params:
                docgen = getattr(callable.__callable__, 'help', None)
                if docgen:
                    return {'message': docgen(self.request)}
                else:
                    return {'message': re.sub('\w\x08', '', render_doc(callable.__callable__))}

            return callable()

class FunctionService(AbstractService):
    def __init__(self, request, function, parent=None, name=None):
        super(FunctionService, self).__init__(request, name or cls.__name__, parent)

        self.function = function

    def process(self):
        # check to see if we're looking for help
        if 'help' in self.request.params:
            docgen = getattr(self.function, 'help', None)
            if docgen:
                return {'message': docgen(self.request)}
            else:
                return {'message': re.sub('\w\x08', '', render_doc(self.function))}

        return self.function(self.request)

class PyObjectService(RestfulService):
    def __init__(self, request, response, parent=None, name=None):
        super(PyObjectService, self).__init__(request, name, parent)

        self.response = response

    def get(self):
        return self.response