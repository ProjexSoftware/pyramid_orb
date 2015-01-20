import orb
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
            id = key

        try:
            record = self.model(id)
        except errors.RecordNotFound:
            if type(id) == int:
                raise
        else:
            return rest.Resource(self.request, record, self)

        method = getattr(self.model, key, None) or \
                 getattr(self.model, projex.text.underscore(key), None) or \
                 getattr(self.model, projex.text.camelHump(key), None)

        if method is None:
            view = self.model.schema().view(key)
            if not view:
                raise KeyError(key)
            else:
                return Collection(self.request, view, parent=self, name=key)
        else:
            # use a classmethod
            if getattr(method, '__lookup__', False):
                return RecordSetCollection(self.request, method(), parent=self, name=method.__name__)
            else:
                raise KeyError(key)

    def get(self):
        info = collect_query_info(self.model, self.request)
        return self.model.select(**info)

    def post(self):
        with orb.Transaction():
            values = collect_params(self.request)
            return self.model.createRecord(**values)

class RecordSetCollection(RestService):
    def __init__(self, request, recordset, parent=None, name=None):
        super(RecordSetCollection, self).__init__(request=request, parent=parent, name=name)

        self.recordset = recordset

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            id = key

        # lookup the table by the id
        try:
            record = self.recordset.table()(id)
        except errors.RecordNotFound:
            if type(id) == int:
                raise
        else:
            if not self.recordset.hasRecord(record):
                raise errors.RecordNotFound(self.recordset.table(), id)
            else:
                return rest.Resource(self.request, record, self)

        # look for a view of this recordset instead
        viewset = self.recordset.view(key)
        if viewset is not None:
            return rest.RecordSetCollection(self.request, viewset, parent=self, name=key)
        else:
            raise KeyError(key)

    def get(self):
        info = collect_query_info(self.recordset.table(), self.request)
        return self.recordset.refine(**info)

    def put(self):
        with orb.Transaction():
            params = collect_params(self.request)
            return self.recordset.update(**params)

    def post(self):
        with orb.Transaction():
            params = collect_params(self.request)
            return self.recordset.createRecord(**params)

class PipeRecordSetCollection(RestService):
    def __init__(self, request, recordset, parent=None, name=None):
        super(PipeRecordSetCollection, self).__init__(request, parent, name=name)

        self.recordset = recordset

    def __getitem__(self, key):
        model = self.recordset.table()
        # look for a record
        try:
            id = int(key)
        except ValueError:
            id = key

        # lookup the table by the id
        try:
            record = self.recordset.table()(id)
        except errors.RecordNotFound:
            if type(id) == int:
                raise
        else:
            if not self.recordset.hasRecord(record):
                raise errors.RecordNotFound(self.recordset.table(), id)
            else:
                return rest.PipedResource(self.request, self.recordset, record, self)

        viewset = self.recordset.view(key)
        if viewset is not None:
            return RecordSetCollection(self.request, viewset, parent=None, name=key)
        else:
            raise KeyError(key)

    def get(self):
        model = self.recordset.table()
        return self.recordset.refine(**collect_query_info(model, self.request))

    def put(self):
        with orb.Transaction():
            params = collect_params(self.request)
            return self.recordset.update(**params)

    def post(self):
        with orb.Transaction():
            params = collect_params(self.request)
            return self.recordset.createRecord(**params)

