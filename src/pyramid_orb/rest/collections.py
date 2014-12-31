import projex.rest
import projex.text

from orb import Query as Q
from orb import errors
from projex.lazymodule import lazy_import
from pyramid_orb.utils import collect_params, collect_query_info

from .service import RestService

rest = lazy_import('pyramid_orb.rest')

class Collection(RestService):
    """ A REST service for collections of data, in this case an ORB model. """
    def __init__(self, request, model, parent=None, name=None, method=None):
        if name is None:
            model_name = projex.text.underscore(model.schema().name())
            name = projex.text.pluralize(model_name)

        super(Collection, self).__init__(request, parent, name=name)

        self.model = model
        self.method = method

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            try:
                method = getattr(self.model, key, None)
            except AttributeError:
                raise KeyError(key)
            else:
                # use a classmethod
                if getattr(method, '__self__', None) == self.model:
                    return RecordSetCollection(self.request, self.model, method, parent=self, name=method.__name__)
                else:
                    raise KeyError(key)
        else:
            info = collect_query_info(self.model, self.request)

            record = self.model(id)
            record.setLookupOptions(info['lookup'])
            record.setDatabaseOptions(info['options'])

            return rest.Resource(self.request, record, self)

    def get(self):
        info = collect_query_info(self.model, self.request)
        return self.model.select(**info)

    def post(self):
        values = collect_params(self.request)
        return self.model.createRecord(**values)

class RecordSetCollection(RestService):
    def __init__(self, request, model, method, parent=None, name=None):
        super(RecordSetCollection, self).__init__(request=request, parent=parent, name=name)

        self.model = model
        self.method = method

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            raise KeyError(key)
        else:
            record = self.method(where=Q(self.model) == id).first()
            if not record:
                raise errors.RecordNotFound(self.model, id)

            info = collect_query_info(self.model, self.request)

            record.setLookupOptions(info['lookup'])
            record.setDatabaseOptions(info['options'])

            return rest.Resource(self.request, record, self)

    def get(self):
        info = collect_query_info(self.model, self.request)
        return self.method(**info)

class PipeCollection(RestService):
    def __init__(self, request, record, pipe, parent=None):
        super(PipeCollection, self).__init__(request, parent, name=pipe.__name__)

        self.pipe = pipe
        self.record = record

    def __getitem__(self, key):
        model = self.pipe.targetReferenceModel()
        # look for a record
        try:
            id = int(key)
        except ValueError:
            raise KeyError(key)
        else:
            record = self.pipe(where=Q(model) == id).first()
            if not record:
                try:
                    record = self.pipe()[id]
                except IndexError:
                    raise errors.RecordNotFound(model, id)

            info = collect_query_info(model, self.request)
            record.setLookupOptions(info['lookup'])
            record.setDatabaseOptions(info['options'])

            if not record:
                raise errors.RecordNotFound(model, key)
            return rest.PipedResource(self.request, self.pipe, record, self)

    def get(self):
        model = self.pipe.targetReferenceModel()
        return self.pipe(**collect_query_info(model, self.request))

    def put(self):
        params = collect_params(self.request)
        return self.pipe().update(**params)

    def post(self):
        params = collect_params(self.request)
        return self.pipe().createRecord(**params)

class ReverseLookupCollection(RestService):
    def __init__(self, request, record, method, parent=None):
        super(ReverseLookupCollection, self).__init__(request, parent, name=method.__name__)

        self.record = record
        self.method = method

    def __getitem__(self, key):
        model = self.method.tableFor(self.record)

        # look for a record
        try:
            record = self.method(where=Q(model) == int(key)).first()
        except ValueError:
            raise KeyError(key)
        else:
            if not record:
                raise errors.RecordNotFound(model, key)

            return rest.Resource(self.request, record, self)

    def get(self):
        info = collect_query_info(self.method.tableFor(self.record), self.request)
        return self.method(**info)

    def put(self):
        params = collect_params(self.request)
        return self.method().update(**params)

    def post(self):
        params = collect_params(self.request)
        return self.method().createRecord(**params)
