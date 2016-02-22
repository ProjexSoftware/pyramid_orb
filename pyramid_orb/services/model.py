import orb

from orb import Query as Q
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_orb.utils import collect_params, get_context, collect_query_info
from .restful import RestfulService


class ModelService(RestfulService):
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

        # reverse lookups and pipes are collection services
        lookup = schema.pipe(key) or schema.reverseLookup(key)
        if lookup:
            if isinstance(lookup, orb.Pipe):
                name = lookup.name()
            else:
                name = lookup.reversed().name

            record = self.model(self.record_id, context=orb.Context(columns=['id']))
            method = getattr(record, name, None)
            if not method:
                raise KeyError(key)
            else:
                from .collection import CollectionService
                records = method(context=get_context(self.request))
                return CollectionService(self.request, records, parent=self)

        # lookup regular method
        method = getattr(self.model, key, None)
        if method:
            return_value = method(context=get_context(self.request, model=self.model))
            if isinstance(return_value, orb.Collection):
                from .collection import CollectionService
                return CollectionService(self.request, return_value, parent=self, name=key)
            elif isinstance(return_value, orb.Model):
                return ModelService(self.request, parent=self, record=return_value)
            else:
                from .builtins import PyObjectService
                return PyObjectService(self.request, return_value, parent=self)
        else:
            return ModelService(self.request, self.model, parent=self, record_id=key)

    @property
    def record(self):
        if self.__record is not None:
            return self.__record
        elif self.record_id is None:
            raise HTTPBadRequest()

        context = get_context(self.request)
        return self.model(self.record_id, context=context)

    def _update(self):
        record = self.record
        values = collect_params(self.request)
        record.update(values)
        record.save()
        return record.__json__()

    def get(self):
        if self.record_id:
            return self.record.__json__()
        else:
            info = collect_query_info(self.model, self.request)
            return self.model.select(**info)

    def patch(self):
        if self.record_id:
            return self._update()
        else:
            raise HTTPBadRequest()

    def post(self):
        if self.record_id:
            raise HTTPBadRequest()
        else:
            values = collect_params(self.request)
            context = get_context(self.request)
            return self.model.create(values, context=context).__json__()

    def put(self):
        if self.record_id:
            return self._update()
        else:
            raise HTTPBadRequest()

    def delete(self):
        if self.record_id:
            context = get_context(self.request)
            if self.from_collection:
                return self.from_collection.remove(self.record_id, context=context)
            else:
                return self.record.delete(context=context)
        else:
            raise HTTPBadRequest()

