import orb
import projex.text

from orb import errors
from pyramid_orb.utils import collect_params, get_context, collect_query_info
from projex.lazymodule import lazy_import

from .service import RestService

rest = lazy_import('pyramid_orb.rest')


class Resource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, record, parent=None):
        super(Resource, self).__init__(request, parent, name=str(id))

        # define custom properties
        self.record = record

    def __getitem__(self, key):
        method = getattr(self.record, key, None) or \
                 getattr(self.record, projex.text.underscore(key), None) or \
                 getattr(self.record, projex.text.camelHump(key), None)

        if not method:
            raise KeyError(key)
        else:
            info = collect_query_info(type(self.record), self.request)

            # load a pipe resource
            if type(method.__func__).__name__ == 'Pipe':
                records = method(**info)
                return rest.PipeRecordSetCollection(self.request, records, self, name=key)
            elif type(method.__func__).__name__ == 'reverselookupmethod':
                records = method(**info)
                return rest.RecordSetCollection(self.request, records, self, name=key)
            elif getattr(method.__func__, '__lookup__', None):
                records = method(**info)
                return rest.RecordSetCollection(self.request, records, self, name=key)
            else:
                column = self.record.schema().column(key)
                if column and column.isReference():
                    return rest.Resource(self.request, method(**info), self)

        raise KeyError(key)

    def get(self):
        return self.record

    def patch(self):
        values = collect_params(self.request)
        with orb.Transaction():
            record = self.record
            record.update(**values)
            record.commit()
            return record

    def put(self):
        values = collect_params(self.request)
        with orb.Transaction():
            record = self.record
            record.update(**values)
            record.commit()
            return record

    def delete(self):
        return self.record.remove()


class PipedResource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, recordset, record, parent=None):
        super(PipedResource, self).__init__(request, parent, name=str(id))

        self.record = record
        self.recordset = recordset

    def get(self):
        return self.record

    def patch(self):
        values = collect_params(self.request)
        with orb.Transaction():
            record = self.record
            record.update(**values)
            record.commit()
            return record

    def put(self):
        values = collect_params(self.request)
        with orb.Transaction():
            record = self.record
            record.update(**values)
            record.commit()
            return record

    def delete(self):
        with orb.Transaction():
            self.recordset.removeRecord(self.record)
            return {}
