import orb
import projex.rest
import projex.text

from orb import errors
from projex.lazymodule import lazy_import
from pyramid_orb.utils import collect_params, collect_query_info, get_context
from pyramid.httpexceptions import HTTPForbidden

from .service import RestService

rest = lazy_import('pyramid_orb.rest')


class ModelService(RestService):
    """ A REST service for collections of data, in this case an ORB model. """
    def __init__(self, request, model, parent=None, name=None, method=None):
        if name is None:
            name = model.schema().dbname()

        super(ModelService, self).__init__(request, parent, name=name)

        acl = getattr(model, '__acl__', None)
        if acl is not None and self.request.method.lower() not in acl:
            raise HTTPForbidden()

        self.model = model
        self.method = method

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            id = key

        context = get_context(self.request)

        try:
            record = self.model(id, context=context)
        except errors.RecordNotFound:
            if type(id) == int:
                raise
        else:
            return rest.RecordService(self.request, record, self)

        method = getattr(self.model, key, None) or \
                 getattr(self.model, projex.text.underscore(key), None) or \
                 getattr(self.model, projex.text.camelHump(key), None)

        if method is None:
            view = self.model.schema().view(key)
            if not view:
                raise KeyError(key)
            else:
                return ModelService(self.request, view, parent=self, name=key)
        else:
            # use a classmethod
            if getattr(method, '__lookup__', False):
                result = method(context=context)
                if isinstance(result, orb.Collection):
                    return CollectionService(self.request, result, parent=self, name=method.__name__)
                elif isinstance(result, orb.Model):
                    return rest.RecordService(self.request, result, self)
                elif result is None:
                    return rest.ObjectService(self.request, {}) # blank JSON object
                else:
                    return rest.ObjectService(self.request, result)
            else:
                raise KeyError(key)

    def get(self):
        info = collect_query_info(self.model, self.request)
        return self.model.select(**info)

    def post(self):
        values = collect_params(self.request)
        context = get_context(self.request)
        return self.model.create(values, context=context)


class CollectionService(RestService):
    def __init__(self, request, records, parent=None, name=None):
        super(CollectionService, self).__init__(request=request, parent=parent, name=name)

        self.model = records.model()
        self.records = records

    def __getitem__(self, key):
        # look for a record
        try:
            id = int(key)
        except ValueError:
            id = key

        context = get_context(self.request)

        # lookup the table by the id
        try:
            record = self.model(id, context=context)
        except errors.RecordNotFound:
            if type(id) == int:
                raise
        else:
            if not self.records.hasRecord(record):
                raise errors.RecordNotFound(self.model, id)
            elif self.records.pipe():
                return rest.PipedRecordService(self.request, record, self)
            else:
                return rest.RecordService(self.request, record, self)

        # look for a view of this records instead
        viewset = self.records.view(key)
        if viewset is not None:
            return rest.CollectionService(self.request, viewset, parent=self, name=key)
        else:
            raise KeyError(key)

    def get(self):
        info = collect_query_info(self.model, self.request)
        return self.records.refine(**info)

    def put(self):
        try:
            values = self.request.json_body
            if type(values) == list:
                values = {'records': values}
        except StandardError:
            values = collect_params(self.request)

        return self.records.update(values)

    def post(self):
        values = collect_params(self.request)
        context = get_context(self.request)
        return self.records.create(values, context=context)

