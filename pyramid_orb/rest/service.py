import orb
import re

from pydoc import render_doc
from pyramid.httpexceptions import HTTPBadRequest


class Service(dict):
    """ Base class for all REST services used within a Pyramid Traversal """
    def __init__(self, request=None, parent=None, name=None):
        super(Service, self).__init__()

        self.request = request
        self.__name__ = name or type(self).__name__
        self.__parent__ = parent

    def add(self, service):
        """
        Adds a sub-service to this instance.  This will store the given service as a sub-tree for this instance.

        :param      service | <pyramid_orb.rest.Service>
        """
        service.__parent__ = self
        self[service.__name__] = service

    def remove(self, service):
        """
        Removes the given service from the list of sub-services available.

        :param      service | <str> || <pyramid_orb.rest.Service>
        """
        try:
            service = self.pop(service.__name__, None)
        except AttributeError:
            service = self.pop(service, None)

        if service:
            service.__parent__ = None

    def process(self):
        raise NotImplementedError

    def permit(self):
        return self.request.method.lower() + '.' + '.'.join(self.request.traversed)


# noinspection PyMethodOverriding
class RestService(Service):
    def delete(self):
        """
        Performs a DELETE operation for this service.

        :return     <dict>
        """
        raise HTTPBadRequest()

    def get(self):
        """
        Performs a GET operation for this service.

        :return     <dict>
        """
        raise HTTPBadRequest()

    def post(self):
        """
        Performs a POST operation for this service.

        :return     <dict>
        """
        raise HTTPBadRequest()

    def patch(self):
        """
        Performs a PATCH operation for this service.

        :return     <dict>
        """
        raise HTTPBadRequest()

    def process(self):
        """
        Process a service using the REST HTTP verbage.

        :param      request | <pyramid.request.Request>

        :return     <dict>
        """
        try:
            method = getattr(self, self.request.method.lower())
        except AttributeError:
            raise HTTPBadRequest()
        else:
            # check to see if we're looking for help
            if 'help' in self.request.params:
                docgen = getattr(method, 'help', None)
                if docgen:
                    return {'message': docgen(self.request)}
                else:
                    return {'message': re.sub('\w\x08', '', render_doc(method))}

            output = method()

            # store additional information in the response header for record sets
            if isinstance(output, orb.Collection):
                new_output = output.__json__()

                if self.request.params.get('paged'):
                    self.request.response.headers['X-Orb-Page'] = str(output.currentPage())
                    self.request.response.headers['X-Orb-Page-Size'] = str(output.pageSize())
                    self.request.response.headers['X-Orb-Start'] = str(output.context().start)
                    self.request.response.headers['X-Orb-Limit'] = str(output.context().limit)
                    self.request.response.headers['X-Orb-Page-Count'] = str(output.pageCount())
                    self.request.response.headers['X-Orb-Total-Count'] = str(output.totalCount())

                output = new_output

            return output


class RestCallable(object):
    def __init__(self, name, callable, method='GET', permit=None):
        self.__name__ = name
        self.__callable__ = callable
        self.__method__ = method
        self.__permit__ = permit

    def __call__(self, request):
        if self.__method__ == request.method:
            return self.__callable__(request)
        else:
            raise StandardError('Invalid request.')

    def get(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return RestCallable(name, callable, 'GET', permit)
        return setup

    def post(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return RestCallable(name, callable, 'POST', permit)
        return setup

    def delete(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return RestCallable(name, callable, 'DELETE', permit)
        return setup

    def put(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return RestCallable(name, callable, 'PUT', permit)
        return setup

    def patch(self, **options):
        def setup(callable):
            name = options.pop('name', self.__name__)
            permit = options.pop('permission', '__DEFAULT__')
            return RestCallable(name, callable, 'PATCH', permit)
        return setup


# noinspection PyMethodOverriding
class ModuleService(Service):
    def __init__(self, request, module, parent=None, name=None):
        super(ModuleService, self).__init__(request, name or module.__name__.split('.')[-1], parent)

        self.module = module
        self.callables = {}
        for callable in vars(module).values():
            if isinstance(callable, RestCallable):
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


# noinspection PyMethodOverriding
class ClassService(Service):
    def __init__(self, request, cls, parent=None, name=None):
        super(ClassService, self).__init__(request, name or cls.__name__, parent)

        self.instance = cls(request)
        self.callables = {}
        for callable in vars(self.instance).values():
            if isinstance(callable, RestCallable):
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

class FunctionService(Service):
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

class ObjectService(RestService):
    def __init__(self, request, response, parent=None, name=None):
        super(ObjectService, self).__init__(request, name, parent)

        self.response = response

    def get(self):
        return self.response