import orb
import projex.text

from pyramid_orb.utils import collect_params, get_context, get_lookup
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
            context = get_context(self.request)
            lookup = get_lookup(self.request)

            # return a resource
            column = self.record.schema().column(key)
            if column and column.isReference():
                return rest.Resource(self.request, method(options=context), self)

            # return a lookup
            elif type(method.__func__).__name__ in ('Pipe', 'reverselookupmethod') or \
                 getattr(method.__func__, '__lookup__', None):

                response = method(expand=lookup.expand, options=context)
                if isinstance(response, orb.RecordSet):
                    return rest.RecordSetCollection(self.request, response, parent=self, name=key)
                elif isinstance(response, orb.Table):
                    return rest.Resource(self.request, response, parent=None)
                elif response is None:
                    return rest.ObjectService(self.request, {})
                else:
                    return rest.ObjectService(self.request, response)

        raise KeyError(key)

    def get(self):
        lookup = get_lookup(self.request)
        return self.record.json(lookup=lookup)

    def patch(self):
        values = collect_params(self.request)
        record = self.record
        record.update(**values)
        record.commit()
        return record

    def put(self):
        values = collect_params(self.request)
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

        self.recordset = recordset
        self.record = record

    def get(self):
        return self.record

    def patch(self):
        values = collect_params(self.request)
        record = self.record
        record.update(**values)
        record.commit()
        return record

    def put(self):
        values = collect_params(self.request)
        record = self.record
        record.update(**values)
        record.commit()
        return record

    def delete(self):
        self.recordset.removeRecord(self.record)
        return {}
