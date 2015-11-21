import inspect
import orb
import projex.text

from pyramid.httpexceptions import HTTPForbidden
from .service import Service, ModuleService, ClassService, FunctionService
from .collections import ModelService


class ApiFactory(dict):
    def __init__(self, version='1.0.0', authenticator=None, analytics=None):
        super(ApiFactory, self).__init__()

        # custom properties
        self._authenticator = authenticator
        self._version = version
        self._analytics = analytics

        # services
        self._factories = {}
        self._models = {}
        self._modules = {}
        self._classes = {}
        self._functions = {}
        self._services = {}

    def analytics(self):
        """
        Returns an implementation of analytics tracking.

        :return     <pyramid_orb.analytics.Analytics> || None
        """
        return self._analytics

    def expose(self, service, name=''):
        """
        Exposes a given service to this API.
        """
        try:
            is_model = issubclass(service, orb.Model)
        except StandardError:
            is_model = False

        # expose a sub-factory
        if isinstance(service, ApiFactory):
            self._factories[name] = service

        # expose an ORB table dynamically as a service
        elif is_model:
            self._models[service.schema().dbname()] = service

        # expose a module dynamically as a service
        elif inspect.ismodule(service):
            if not name:
                name = service.__name__.split('.')[-1]

            self._modules[name] = service

        # expose a class dynamically as a service
        elif inspect.isclass(service):
            if not name:
                name = service.__name__

            self._classes[name] = service

        # expose a function dynamically as a service
        elif inspect.isfunction(service):
            if not name:
                name = service.__name__

            self._functions[name] = service

        # expose a service directly
        else:
            if not name:
                name = service.__name__

            self._services[name] = service

    def factory(self, request):
        """
        Returns a new service for the inputted request.

        :param      request | <pyramid.request.Request>

        :return     <pyramid_orb.rest.Service>
        """
        service = Service(request)

        # create dynamic factory resources
        for name, factory in self._factories.items():
            sub_api = factory.factory(request)
            service[name] = sub_api

        # create dynamic services based on exposed modules
        for name, module in self._modules.items():
            service[name] = ModuleService(request, module, parent=service, name=name)

        # create dynamic services based on an exposed class
        for name, cls in self._classes.items():
            service[name] = ClassService(request, cls, parent=service, name=name)

        # create dynamic services based on an exposed function
        for name, func in self._functions.items():
            service[name] = FunctionService(request, func, parent=service, name=name)

        # create dynamic services based on exposed models
        for name, model in self._models.items():
            # define the service
            service[name] = ModelService(request, model, parent=service, name=name)

        # create static services
        for name, sub_service in self._services.items():
            service[name] = sub_service(request, parent=service, name=name)

        request.api_service = service
        return service

    def process(self, request):
        # look for a request to the root of the API, this will generate the
        # help information for the system
        if not request.traversed:
            return {}

        # otherwise, process the request context
        else:
            if self.analytics():
                self.analytics().report(request)

            if not self.testPermits(request, request.context.permit()):
                raise HTTPForbidden()

            return request.context.process()

    def serve(self, config, path, route_name=None, **view_options):
        """
        Serves this API from the inputted root path
        """
        route_name = route_name or path.replace('/', '.').strip('.')
        path = path.strip('/') + '/*traverse'

        # configure the route and the path
        config.add_route(route_name, path, factory=self.factory)
        config.add_view(self.process, route_name=route_name, renderer='json2', **view_options)

    def testPermits(self, request, permission):
        """
        Tests whether or not the active user has access to the given permission.

        :param      permission | <str>

        :return     <bool>
        """
        if self._authenticator:
            return self._authenticator(request, permission)
        return True

