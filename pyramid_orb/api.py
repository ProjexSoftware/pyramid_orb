import inspect
import orb
import projex.text

from pyramid_restful.api import ApiFactory
from .services import ModelService


class OrbApiFactory(ApiFactory):
    def register(self, service, name=''):
        """
        Exposes a given service to this API.
        """
        try:
            is_model = issubclass(service, orb.Model)
        except StandardError:
            is_model = False

        # expose an ORB table dynamically as a service
        if is_model:
            self._ApiFactory__services[service.schema().dbname()] = (ModelService, service)

        else:
            super(OrbApiFactory, self).register(service, name=name)

