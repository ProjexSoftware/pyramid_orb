import orb
import projex.text

from pyramid_orb.utils import collect_params, get_context
from projex.lazymodule import lazy_import

from .service import RestService

rest = lazy_import('pyramid_orb.rest')


class RecordService(RestService):
    """ Represents an individual database record """
    def __init__(self, request, record, parent=None):
        super(RecordService, self).__init__(request, parent, name=str(id))

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

            # return a resource
            column = self.record.schema().column(key)
            if column and column.isReference():
                return rest.RecordResource(self.request, method(context=context), self)

            # return a lookup
            elif getattr(method.__func__, '__lookup__', None):

                response = method(context=context)
                if isinstance(response, orb.Collection):
                    return rest.CollectionService(self.request, response, parent=self, name=key)
                elif isinstance(response, orb.Model):
                    return rest.ModelResource(self.request, response, parent=None)
                elif response is None:
                    return rest.ObjectService(self.request, {})
                else:
                    return rest.ObjectService(self.request, response)

        raise KeyError(key)

    def get(self):
        return self.record.__json__()

    def patch(self):
        values = collect_params(self.request)
        record = self.record
        record.update(values)
        record.save()
        return record

    def put(self):
        values = collect_params(self.request)
        record = self.record
        record.update(values)
        record.save()
        return record

    def delete(self):
        return self.record.delete()


class PipedRecordResource(RestService):
    """ Represents an individual database record """
    def __init__(self, request, collection, record, parent=None):
        super(PipedRecordResource, self).__init__(request, parent, name=str(id))

        self.collection = collection
        self.record = record

    def get(self):
        return self.record

    def patch(self):
        values = collect_params(self.request)
        record = self.record
        record.update(values)
        record.save()
        return record

    def put(self):
        values = collect_params(self.request)
        record = self.record
        record.update(**values)
        record.save()
        return record

    def delete(self):
        self.collection.remove(self.record)
        return {}
