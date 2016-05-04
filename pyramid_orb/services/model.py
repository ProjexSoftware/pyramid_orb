import orb
import projex.text

from orb import Query as Q
from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden
from pyramid_orb.utils import get_context
from pyramid_orb.service import OrbService


class ModelService(OrbService):
    """ Represents an individual database record """
    def __init__(self, request, model, parent=None, record_id=None, from_collection=None, record=None, name=None):
        name = name or str(id)
        super(ModelService, self).__init__(request, parent, name=name)

        # define custom properties
        self.model = model
        self.record_id = record_id
        self.__record = record
        self.from_collection = from_collection

    def __getitem__(self, key):
        schema = self.model.schema()

        # lookup the articles information
        col = schema.column(key, raise_=False)
        if col:
            # return a reference for the collection
            if isinstance(col, orb.ReferenceColumn):
                record_id = self.model.select(where=Q(self.model) == self.record_id, limit=1).values(col.name())[0]
                return ModelService(self.request, col.referenceModel(), record_id=record_id)

            # columns are not directly accessible
            else:
                raise KeyError(key)

        # generate collector services
        lookup = schema.collector(key)
        if lookup:
            name = lookup.name()
            if not lookup.testFlag(lookup.Flags.Static):
                _, context = get_context(self.request, model=self.model)
                context.where = None
                record = self.model(self.record_id, context=context)
                method = getattr(record, name, None)
            else:
                method = getattr(self.model, name, None)

            if not method:
                raise KeyError(key)
            else:
                from .collection import CollectionService
                values, context = get_context(self.request, model=lookup.model())
                if values:
                    where = orb.Query.build(values)
                    context.where = where & context.where

                record.setContext(context)
                records = method(context=context)
                return CollectionService(self.request, records, parent=self)

        # make sure we're not trying to load a property we don't have
        elif self.record_id:
            raise KeyError(key)

        # otherwise, return a model based on the id
        return ModelService(self.request, self.model, parent=self, record_id=key)

    def _update(self):
        values, context = get_context(self.request, model=self.model)
        record = self.model(self.record_id, context=context)
        record.update(values)
        record.save()
        return record.__json__()

    def get(self):
        values, context = get_context(self.request, model=self.model)
        if context.returning == 'schema':
            return self.model.schema()
        elif self.record_id:
            return self.model(self.record_id, context=context)
        else:
            # convert values to query parameters
            if values:
                where = orb.Query.build(values)
                context.where = where & context.where

            # grab search terms or query
            search_terms = self.request.params.get('terms') or self.request.params.get('q')

            if search_terms:
                return self.model.search(search_terms, context=context)
            else:
                return self.model.select(context=context)

    def patch(self):
        if self.record_id:
            return self._update()
        else:
            raise HTTPBadRequest()

    def post(self):
        if self.record_id:
            raise HTTPBadRequest()
        else:
            values, context = get_context(self.request, model=self.model)
            record = self.model.create(values, context=context)
            return record.__json__()

    def put(self):
        if self.record_id:
            return self._update()
        else:
            raise HTTPBadRequest()

    def delete(self):
        if self.record_id:
            values, context = get_context(self.request, model=self.model)
            if self.from_collection:
                return self.from_collection.remove(self.record_id, context=context)
            else:
                record = self.model(self.record_id, context=context)
                record.delete()
                return record
        else:
            raise HTTPBadRequest()

    def permitted(self):
        method = self.request.method.lower()
        auth = getattr(self.model, '__auth__', None)

        if callable(auth):
            return auth(scope={'request': self.request})

        elif isinstance(auth, dict):
            try:
                method_auth = auth[method]
            except KeyError:
                raise HTTPForbidden()
            else:
                if callable(method_auth):
                    return method_auth(self.request)
                elif method_auth:
                    return self.request.has_permission(method_auth)
                else:
                    return True

        elif isinstance(auth, (list, tuple, set)):
            return method in auth

        elif auth:
            return self.request.has_permission(auth)

        else:
            return True

    @classmethod
    def routes(cls, obj):
        root = obj.schema().dbname()
        output = {
            '/{0}'.format(root): 'get,post',
            '/{0}/{{id}}'.format(root): 'get,patch,put,delete'
        }

        for collector in obj.schema().collectors().values():
            model = collector.model()
            if model:
                rev_type = projex.text.underscore(model.schema().name())
            else:
                rev_type = 'model'

            collector_path = '/{0}/{{id}}/{1}'.format(root, collector.name())
            output[collector_path] = 'get,post,put'
            output[collector_path + '/{{{0}:id}}'.format(rev_type)] = 'get,delete'

        return output