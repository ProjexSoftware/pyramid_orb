import orb
import re

from .abstract import AbstractService
from pydoc import render_doc
from pyramid.httpexceptions import HTTPBadRequest


# noinspection PyMethodOverriding
class RestfulService(AbstractService):
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
