
from pyramid_orb.utils import collect_params
from projex.lazymodule import lazy_import
from pyramid_orb.utils import collect_query_info

from .service import RestService

rest = lazy_import('pyramid_orb.rest')

class Resource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, record, parent=None):
        super(Resource, self).__init__(request, parent, name=str(record.id()))

        self.record = record

    def __getitem__(self, key):
        try:
            method = getattr(self.record, key)
        except AttributeError:
            raise KeyError(key)
        else:
            # load a pipe resource
            if type(method.__func__).__name__ == 'Pipe':
                return rest.PipeCollection(self.request, self.record, method, self)
            elif type(method.__func__).__name__ == 'reverselookupmethod':
                return rest.ReverseLookupCollection(self.request, self.record, method, self)
            else:
                column = self.record.schema().column(key)
                if column and column.isReference():
                    return rest.Resource(self.request, method(), self)

        raise KeyError(key)

    def get(self):
        return self.record

    def patch(self):
        params = collect_params(self.request)
        self.record.update(**params)
        self.record.commit()
        return self.record

    def put(self):
        params = collect_params(self.request)
        self.record.update(**params)
        self.record.commit()
        return self.record

    def delete(self):
        return self.record.remove()


class PipedResource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, pipe, record, parent=None):
        super(PipedResource, self).__init__(request, parent, name=str(record.id()))

        self.pipe = pipe
        self.record = record

    def get(self):
        return self.record

    def patch(self):
        params = collect_params(self.request)
        self.record.update(**params)
        self.record.commit()
        return self.record

    def put(self):
        params = collect_params(self.request)
        self.record.update(**params)
        self.record.commit()
        return self.record

    def delete(self):
        self.pipe().removeRecord(self.record)
        return {}
