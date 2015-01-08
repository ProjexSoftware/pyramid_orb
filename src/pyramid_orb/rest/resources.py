import orb

from pyramid_orb.utils import collect_params
from projex.lazymodule import lazy_import

from .service import RestService

rest = lazy_import('pyramid_orb.rest')

class Resource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, record, parent=None):
        id = record.id() if (orb.Table.recordcheck(record) or orb.View.recordcheck(record)) else record.get('id', 'None')
        super(Resource, self).__init__(request, parent, name=str(id))

        self.record = record

    def __getitem__(self, key):
        try:
            method = getattr(self.record, key)
        except AttributeError:
            raise KeyError(key)
        else:
            # load a pipe resource
            if type(method.__func__).__name__ == 'Pipe':
                return rest.PipeRecordSetCollection(self.request, method(), self, name=key)
            elif type(method.__func__).__name__ == 'reverselookupmethod':
                return rest.RecordSetCollection(self.request, method(), self, name=key)
            elif getattr(method.__func__, '__lookup__', None):
                return rest.RecordSetCollection(self.request, method(), self, name=key)
            else:
                column = self.record.schema().column(key)
                if column and column.isReference():
                    return rest.Resource(self.request, method(), self)

        raise KeyError(key)

    def get(self):
        self.record.updateOptions(**collect_params(self.request))
        return self.record

    def patch(self):
        with orb.Transaction():
            params = collect_params(self.request)
            self.record.update(**params)
            self.record.commit()
        return self.record

    def put(self):
        params = collect_params(self.request)
        with orb.Transaction():
            self.record.update(**params)
            self.record.commit()
        return self.record

    def delete(self):
        return self.record.remove()


class PipedResource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, recordset, record, parent=None):
        super(PipedResource, self).__init__(request, parent, name=str(record.id()))

        self.recordset = recordset
        self.record = record

    def get(self):
        self.record.updateOptions(**collect_params(self.request))
        return self.record

    def patch(self):
        params = collect_params(self.request)
        with orb.Transaction():
            self.record.update(**params)
            self.record.commit()
        return self.record

    def put(self):
        params = collect_params(self.request)
        with orb.Transaction():
            self.record.update(**params)
            self.record.commit()
        return self.record

    def delete(self):
        with orb.Transaction():
            self.recordset.removeRecord(self.record)
        return {}
