from pyramid.httpexceptions import HTTPBadRequest

class Service(dict):
    """ Base class for all REST services used within a Pyramid Traversal """
    def __init__(self, request=None, parent=None, name=None):
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

    def process(self, request):
        raise NotImplementedError


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
            return method()

class ModuleService(Service):
    def __init__(self, request, module, parent=None, name=None):
        super(ModuleService, self).__init__(request, name or module.__name__, parent)

        self.module = module

    def process(self):
        print self.request.path

class ClassService(Service):
    def __init__(self, request, cls, parent=None, name=None):
        super(ClassService, self).__init__(request, name or cls.__name__, parent)

        self.instance = cls(request)