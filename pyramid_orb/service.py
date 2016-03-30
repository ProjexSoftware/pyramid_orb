import orb
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden


class OrbService(object):
    def __init__(self, request=None, parent=None, name=None):
        self.__name__ = name or type(self).__name__
        self.__parent__ = parent
        self.request = request

    def __getitem__(self, key):
        raise KeyError

    def process(self):
        method = self.request.method.lower()
        try:
            func = getattr(self, method)
        except AttributeError:
            raise HTTPNotFound()
        else:
            permit = self.permission()
            if permit and not self.request.has_permission(permit):
                raise HTTPForbidden()
            else:
                output = func()

                # store additional information in the response header for record sets
                if isinstance(output, orb.Collection):
                    if self.request.params.get('paged'):
                        self.request.response.headers['X-Orb-Page'] = str(output.currentPage())
                        self.request.response.headers['X-Orb-Page-Size'] = str(output.pageSize())
                        self.request.response.headers['X-Orb-Start'] = str(output.context().start)
                        self.request.response.headers['X-Orb-Limit'] = str(output.context().limit)
                        self.request.response.headers['X-Orb-Page-Count'] = str(output.pageCount())
                        self.request.response.headers['X-Orb-Total-Count'] = str(output.totalCount())

                    return output
                else:
                    return output

    def permission(self):
        return None